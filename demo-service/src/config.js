require('dotenv').config();

module.exports = {
  // Server
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',

  // CORS
  corsOrigin: process.env.CORS_ORIGIN || '*',

  // Database
  databaseUrl: process.env.DATABASE_URL,

  // Redis
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',

  // Steam
  steam: {
    username: process.env.STEAM_USERNAME,
    password: process.env.STEAM_PASSWORD,
  },

  // Demo Storage
  demosPath: process.env.DEMOS_PATH || './demos',

  // Cleanup
  cleanup: {
    enabled: process.env.CLEANUP_ENABLED === 'true',
    days: parseInt(process.env.CLEANUP_DAYS) || 30,
    intervalHours: parseInt(process.env.CLEANUP_INTERVAL_HOURS) || 24,
  },

  // Webhook
  webhook: {
    enabled: process.env.WEBHOOK_ENABLED === 'true',
    url: process.env.WEBHOOK_URL,
    secret: process.env.WEBHOOK_SECRET,
  },
};
