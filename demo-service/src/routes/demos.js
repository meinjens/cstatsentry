const express = require('express');
const demoService = require('../services/demoService');
const logger = require('../utils/logger');

const router = express.Router();

/**
 * POST /api/demos
 * Create a new demo download request
 */
router.post('/', async (req, res) => {
  const { sharecode } = req.body;

  if (!sharecode) {
    return res.status(400).json({ error: 'Sharecode is required' });
  }

  const demo = await demoService.createDemo(sharecode);

  res.status(201).json(demo);
});

/**
 * GET /api/demos
 * List all demos
 */
router.get('/', async (req, res) => {
  const filters = {
    status: req.query.status,
    limit: parseInt(req.query.limit) || 50,
    offset: parseInt(req.query.offset) || 0,
  };

  const demos = await demoService.getDemos(filters);

  res.json({
    demos,
    count: demos.length,
  });
});

/**
 * GET /api/demos/stats
 * Get statistics
 */
router.get('/stats', async (req, res) => {
  const stats = await demoService.getStats();
  res.json(stats);
});

/**
 * GET /api/demos/:id
 * Get demo details
 */
router.get('/:id', async (req, res) => {
  const demo = await demoService.getDemoById(req.params.id);
  res.json(demo);
});

/**
 * GET /api/demos/:id/file
 * Download demo file
 */
router.get('/:id/file', async (req, res) => {
  const filePath = await demoService.getDemoFilePath(req.params.id);
  const demo = await demoService.getDemoById(req.params.id);

  const fileName = `${demo.matchId || 'demo'}.dem.bz2`;

  res.download(filePath, fileName, (err) => {
    if (err) {
      logger.error('Error sending file:', err);
    }
  });
});

/**
 * DELETE /api/demos/:id
 * Delete a demo
 */
router.delete('/:id', async (req, res) => {
  const result = await demoService.deleteDemo(req.params.id);
  res.json(result);
});

module.exports = router;
