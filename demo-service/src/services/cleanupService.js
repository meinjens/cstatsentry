const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const logger = require('../utils/logger');
const config = require('../config');

const prisma = new PrismaClient();

class CleanupService {
  constructor() {
    this.intervalId = null;
  }

  /**
   * Start automatic cleanup
   */
  start() {
    if (!config.cleanup.enabled) {
      logger.info('Auto-cleanup is disabled');
      return;
    }

    logger.info(`Starting auto-cleanup service (every ${config.cleanup.intervalHours} hours, delete demos older than ${config.cleanup.days} days)`);

    // Run immediately
    this.runCleanup();

    // Schedule periodic cleanup
    const intervalMs = config.cleanup.intervalHours * 60 * 60 * 1000;
    this.intervalId = setInterval(() => {
      this.runCleanup();
    }, intervalMs);
  }

  /**
   * Stop automatic cleanup
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      logger.info('Auto-cleanup service stopped');
    }
  }

  /**
   * Run cleanup process
   */
  async runCleanup() {
    try {
      logger.info('Running cleanup...');

      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - config.cleanup.days);

      // Find old completed demos
      const oldDemos = await prisma.demo.findMany({
        where: {
          status: 'COMPLETED',
          downloadedAt: {
            lt: cutoffDate,
          },
        },
      });

      logger.info(`Found ${oldDemos.length} old demos to cleanup`);

      let deletedCount = 0;
      let errorCount = 0;

      for (const demo of oldDemos) {
        try {
          // Delete file if exists
          if (demo.filePath && fs.existsSync(demo.filePath)) {
            fs.unlinkSync(demo.filePath);
            logger.debug(`Deleted file: ${demo.filePath}`);
          }

          // Delete from database
          await prisma.demo.delete({
            where: { id: demo.id },
          });

          deletedCount++;
        } catch (error) {
          logger.error(`Error deleting demo ${demo.id}:`, error);
          errorCount++;
        }
      }

      logger.info(`Cleanup completed: ${deletedCount} deleted, ${errorCount} errors`);

      return { deleted: deletedCount, errors: errorCount };

    } catch (error) {
      logger.error('Cleanup error:', error);
      throw error;
    }
  }
}

module.exports = new CleanupService();
