const { PrismaClient } = require('@prisma/client');
const axios = require('axios');
const crypto = require('crypto');
const logger = require('../utils/logger');
const config = require('../config');

const prisma = new PrismaClient();

class WebhookService {
  /**
   * Send webhook notification for a demo
   */
  async sendWebhook(demoId) {
    if (!config.webhook.enabled || !config.webhook.url) {
      return;
    }

    try {
      // Get demo details
      const demo = await prisma.demo.findUnique({
        where: { id: demoId },
      });

      if (!demo) {
        logger.error(`Demo ${demoId} not found for webhook`);
        return;
      }

      // Create webhook record
      const webhook = await prisma.webhook.create({
        data: {
          demoId: demo.id,
          url: config.webhook.url,
          status: 'PENDING',
        },
      });

      // Prepare payload
      const payload = {
        event: 'demo.completed',
        demoId: demo.id,
        sharecode: demo.sharecode,
        matchId: demo.matchId,
        status: demo.status,
        downloadedAt: demo.downloadedAt,
      };

      // Generate signature if secret is configured
      let signature = null;
      if (config.webhook.secret) {
        const hmac = crypto.createHmac('sha256', config.webhook.secret);
        hmac.update(JSON.stringify(payload));
        signature = hmac.digest('hex');
      }

      // Send webhook
      const headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'CS2-Demo-Downloader/1.0',
      };

      if (signature) {
        headers['X-Webhook-Signature'] = signature;
      }

      logger.info(`Sending webhook for demo ${demoId} to ${config.webhook.url}`);

      const response = await axios.post(config.webhook.url, payload, {
        headers,
        timeout: 10000,
      });

      // Update webhook as sent
      await prisma.webhook.update({
        where: { id: webhook.id },
        data: {
          status: 'SENT',
          attempts: 1,
          lastAttempt: new Date(),
          response: `${response.status} ${response.statusText}`,
        },
      });

      logger.info(`Webhook sent successfully for demo ${demoId}`);

    } catch (error) {
      logger.error(`Webhook error for demo ${demoId}:`, error);

      // Update webhook as failed
      await prisma.webhook.updateMany({
        where: {
          demoId: demoId,
          status: 'PENDING',
        },
        data: {
          status: 'FAILED',
          attempts: 1,
          lastAttempt: new Date(),
          response: error.message,
        },
      });
    }
  }

  /**
   * Retry failed webhooks
   */
  async retryFailedWebhooks() {
    const failedWebhooks = await prisma.webhook.findMany({
      where: {
        status: 'FAILED',
        attempts: {
          lt: 3,
        },
      },
      take: 10,
    });

    logger.info(`Retrying ${failedWebhooks.length} failed webhooks`);

    for (const webhook of failedWebhooks) {
      await this.sendWebhook(webhook.demoId);
    }
  }
}

module.exports = new WebhookService();
