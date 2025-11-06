const { PrismaClient } = require('@prisma/client');
const { v4: uuidv4 } = require('uuid');
const downloadQueue = require('../queue/downloadQueue');
const logger = require('../utils/logger');
const { NotFoundError, ConflictError, ValidationError } = require('../utils/errors');
const fs = require('fs');

const prisma = new PrismaClient();

class DemoService {
  /**
   * Create a new demo download request
   */
  async createDemo(sharecode) {
    // Validate sharecode format
    const sharecodePattern = /^CSGO(-?[\w]{5}){5}$/;
    if (!sharecodePattern.test(sharecode)) {
      throw new ValidationError('Invalid sharecode format');
    }

    // Check if demo already exists
    const existing = await prisma.demo.findUnique({
      where: { sharecode },
    });

    if (existing) {
      throw new ConflictError('Demo with this sharecode already exists');
    }

    // Create demo record
    const demo = await prisma.demo.create({
      data: {
        id: uuidv4(),
        sharecode,
        status: 'PENDING',
      },
    });

    logger.info(`Created demo ${demo.id} for sharecode ${sharecode}`);

    // Add to download queue
    await downloadQueue.add({
      demoId: demo.id,
      sharecode,
    });

    return demo;
  }

  /**
   * Get all demos with optional filters
   */
  async getDemos(filters = {}) {
    const where = {};

    if (filters.status) {
      where.status = filters.status;
    }

    const demos = await prisma.demo.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: filters.limit || 50,
      skip: filters.offset || 0,
    });

    // Convert BigInt to string for JSON serialization
    return demos.map(demo => ({
      ...demo,
      fileSize: demo.fileSize ? demo.fileSize.toString() : null,
    }));
  }

  /**
   * Get demo by ID
   */
  async getDemoById(id) {
    const demo = await prisma.demo.findUnique({
      where: { id },
    });

    if (!demo) {
      throw new NotFoundError('Demo not found');
    }

    // Convert BigInt to string
    return {
      ...demo,
      fileSize: demo.fileSize ? demo.fileSize.toString() : null,
    };
  }

  /**
   * Delete demo by ID
   */
  async deleteDemo(id) {
    const demo = await prisma.demo.findUnique({
      where: { id },
    });

    if (!demo) {
      throw new NotFoundError('Demo not found');
    }

    // Delete file if exists
    if (demo.filePath && fs.existsSync(demo.filePath)) {
      fs.unlinkSync(demo.filePath);
      logger.info(`Deleted file: ${demo.filePath}`);
    }

    // Delete from database
    await prisma.demo.delete({
      where: { id },
    });

    logger.info(`Deleted demo ${id}`);

    return { success: true };
  }

  /**
   * Get demo file path
   */
  async getDemoFilePath(id) {
    const demo = await prisma.demo.findUnique({
      where: { id },
    });

    if (!demo) {
      throw new NotFoundError('Demo not found');
    }

    if (demo.status !== 'COMPLETED') {
      throw new ValidationError('Demo is not ready for download');
    }

    if (!demo.filePath || !fs.existsSync(demo.filePath)) {
      throw new NotFoundError('Demo file not found');
    }

    return demo.filePath;
  }

  /**
   * Get statistics
   */
  async getStats() {
    const [total, pending, downloading, completed, failed] = await Promise.all([
      prisma.demo.count(),
      prisma.demo.count({ where: { status: 'PENDING' } }),
      prisma.demo.count({ where: { status: 'DOWNLOADING' } }),
      prisma.demo.count({ where: { status: 'COMPLETED' } }),
      prisma.demo.count({ where: { status: 'FAILED' } }),
    ]);

    return {
      total,
      pending,
      downloading,
      completed,
      failed,
    };
  }
}

module.exports = new DemoService();
