const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { PrismaClient } = require('@prisma/client');
const downloadQueue = require('./downloadQueue');
const gcClient = require('../steam/gcClient');
const logger = require('../utils/logger');
const config = require('../config');

const prisma = new PrismaClient();

// Ensure demos directory exists
if (!fs.existsSync(config.demosPath)) {
  fs.mkdirSync(config.demosPath, { recursive: true });
}

// Process download jobs
downloadQueue.process(async (job) => {
  const { demoId, sharecode } = job.data;

  logger.info(`Processing demo download job: ${demoId}`);

  try {
    // Update status to FETCHING_URL
    await prisma.demo.update({
      where: { id: demoId },
      data: { status: 'FETCHING_URL' },
    });

    // Get GC client and request demo URL
    const gc = gcClient.getInstance();
    const matchInfo = await gc.requestDemoUrl(sharecode);

    logger.info(`Got demo URL: ${matchInfo.demoUrl}`);

    // Update demo with match info
    await prisma.demo.update({
      where: { id: demoId },
      data: {
        matchId: matchInfo.matchId,
        matchDate: matchInfo.matchDate,
        demoUrl: matchInfo.demoUrl,
        duration: matchInfo.duration,
        score: matchInfo.score,
        gameType: matchInfo.gameType,
        players: matchInfo.players || [],
        status: 'DOWNLOADING',
      },
    });

    // Download demo file
    const fileName = `${matchInfo.matchId}.dem.bz2`;
    const filePath = path.join(config.demosPath, fileName);

    logger.info(`Downloading demo file to: ${filePath}`);

    const response = await axios({
      method: 'GET',
      url: matchInfo.demoUrl,
      responseType: 'stream',
    });

    const writer = fs.createWriteStream(filePath);

    response.data.pipe(writer);

    await new Promise((resolve, reject) => {
      writer.on('finish', resolve);
      writer.on('error', reject);
    });

    // Get file size
    const stats = fs.statSync(filePath);
    const fileSize = stats.size;

    logger.info(`Demo downloaded successfully. Size: ${fileSize} bytes`);

    // Update demo as completed
    await prisma.demo.update({
      where: { id: demoId },
      data: {
        status: 'COMPLETED',
        filePath: filePath,
        fileSize: BigInt(fileSize),
        downloadedAt: new Date(),
      },
    });

    // Trigger webhook if enabled
    if (config.webhook.enabled) {
      const webhookService = require('../services/webhookService');
      await webhookService.sendWebhook(demoId);
    }

    return { success: true, demoId };

  } catch (error) {
    logger.error(`Error processing demo ${demoId}:`, error);

    // Update demo as failed
    await prisma.demo.update({
      where: { id: demoId },
      data: {
        status: 'FAILED',
        error: error.message,
      },
    });

    throw error;
  }
});

logger.info('Download worker started');

module.exports = downloadQueue;
