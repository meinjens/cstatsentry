require('express-async-errors');
const express = require('express');
const cors = require('cors');
const config = require('./config');
const logger = require('./utils/logger');
const { errorHandler } = require('./utils/errors');
const demosRouter = require('./routes/demos');
const cleanupService = require('./services/cleanupService');
const gcClient = require('./steam/gcClient');

// Import worker to start processing
require('./queue/worker');

// Create Express app
const app = express();

// Middleware
app.use(cors({
  origin: config.corsOrigin === '*' ? '*' : config.corsOrigin.split(',').map(o => o.trim()),
  credentials: true,
}));
app.use(express.json());

// Request logging
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.url}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// API routes
app.use('/api/demos', demosRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Error handler
app.use(errorHandler);

// Start server
const server = app.listen(config.port, async () => {
  logger.info(`Server running on port ${config.port}`);
  logger.info(`Environment: ${config.nodeEnv}`);

  // Connect to Steam/GC
  try {
    logger.info('Connecting to Steam and CS2 Game Coordinator...');
    const gc = gcClient.getInstance();
    await gc.connect();
    logger.info('✓ Connected to Steam and GC successfully');
  } catch (error) {
    logger.error('Failed to connect to Steam/GC:', error);
    logger.warn('Server will continue but demo downloads will fail');
  }

  // Start cleanup service
  cleanupService.start();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully...');

  cleanupService.stop();

  server.close(() => {
    logger.info('Server closed');

    const gc = gcClient.getInstance();
    gc.disconnect();

    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully...');

  cleanupService.stop();

  server.close(() => {
    logger.info('Server closed');

    const gc = gcClient.getInstance();
    gc.disconnect();

    process.exit(0);
  });
});

module.exports = app;
