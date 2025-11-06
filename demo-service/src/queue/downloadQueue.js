const Queue = require('bull');
const config = require('../config');
const logger = require('../utils/logger');

// Create Bull queue
const downloadQueue = new Queue('demo-downloads', config.redisUrl, {
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: true,
    removeOnFail: false,
  },
});

// Queue event handlers
downloadQueue.on('error', (error) => {
  logger.error('Queue error:', error);
});

downloadQueue.on('failed', (job, err) => {
  logger.error(`Job ${job.id} failed:`, err);
});

downloadQueue.on('completed', (job) => {
  logger.info(`Job ${job.id} completed successfully`);
});

module.exports = downloadQueue;
