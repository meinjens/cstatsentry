const SteamUser = require('steam-user');
const GlobalOffensive = require('globaloffensive');
const EventEmitter = require('events');
const logger = require('../utils/logger');
const config = require('../config');

class GCClient extends EventEmitter {
  constructor() {
    super();
    this.steamClient = null;
    this.csgoClient = null;
    this.ready = false;
    this.connecting = false;
  }

  async connect() {
    if (this.ready) {
      return;
    }

    if (this.connecting) {
      // Wait for existing connection attempt
      return new Promise((resolve) => {
        this.once('ready', resolve);
      });
    }

    this.connecting = true;
    logger.info('Connecting to Steam...');

    return new Promise((resolve, reject) => {
      this.steamClient = new SteamUser();
      this.csgoClient = new GlobalOffensive(this.steamClient);

      // Steam events
      this.steamClient.on('loggedOn', () => {
        logger.info('✓ Logged into Steam');
        logger.info('Launching CS2...');
        this.steamClient.gamesPlayed([730]); // CS2 App ID
      });

      this.steamClient.on('error', (err) => {
        logger.error('Steam error:', err);
        this.connecting = false;
        reject(err);
      });

      // CS2 GC events
      this.csgoClient.on('connectedToGC', () => {
        logger.info('✓✓✓ Connected to CS2 Game Coordinator!');
        this.ready = true;
        this.connecting = false;
        this.emit('ready');
        resolve();
      });

      this.csgoClient.on('disconnectedFromGC', (reason) => {
        logger.warn('Disconnected from GC:', reason);
        this.ready = false;
      });

      // Login
      this.steamClient.logOn({
        accountName: config.steam.username,
        password: config.steam.password,
      });

      // Timeout after 60 seconds
      setTimeout(() => {
        if (!this.ready) {
          this.connecting = false;
          reject(new Error('Timeout: GC connection failed'));
        }
      }, 60000);
    });
  }

  async requestDemoUrl(sharecode) {
    if (!this.ready) {
      await this.connect();
    }

    return new Promise((resolve, reject) => {
      logger.info(`Requesting demo URL for sharecode: ${sharecode}`);

      const timeout = setTimeout(() => {
        reject(new Error('Timeout: No response from GC'));
      }, 15000);

      this.csgoClient.once('matchList', (matches) => {
        clearTimeout(timeout);

        if (!matches || !Array.isArray(matches) || matches.length === 0) {
          return reject(new Error('No match data received'));
        }

        const match = matches[0];

        // Extract demo URL from last roundstats
        let demoUrl = null;
        if (match.roundstatsall && match.roundstatsall.length > 0) {
          const lastRound = match.roundstatsall[match.roundstatsall.length - 1];
          demoUrl = lastRound.map;
        }

        if (!demoUrl) {
          return reject(new Error('No demo URL found in match data'));
        }

        // Extract match info
        const matchInfo = {
          matchId: match.matchid,
          matchDate: match.matchtime ? new Date(match.matchtime * 1000) : null,
          demoUrl: demoUrl,
          duration: match.roundstatsall[match.roundstatsall.length - 1].match_duration,
        };

        // Extract map and game type from last round
        const lastRound = match.roundstatsall[match.roundstatsall.length - 1];
        if (lastRound.reservation) {
          matchInfo.gameType = lastRound.reservation.game_type;
        }

        // Calculate score
        if (lastRound.team_scores && lastRound.team_scores.length === 2) {
          matchInfo.score = `${lastRound.team_scores[0]}-${lastRound.team_scores[1]}`;
        }

        // Extract players info
        if (lastRound.reservation && lastRound.reservation.account_ids) {
          matchInfo.players = lastRound.reservation.account_ids.map((accountId, index) => ({
            accountId: accountId,
            kills: lastRound.enemy_kills ? lastRound.enemy_kills[index] : 0,
            deaths: lastRound.deaths ? lastRound.deaths[index] : 0,
            assists: lastRound.assists ? lastRound.assists[index] : 0,
            mvps: lastRound.mvps ? lastRound.mvps[index] : 0,
            headshots: lastRound.enemy_headshots ? lastRound.enemy_headshots[index] : 0,
          }));
        }

        logger.info('Demo URL retrieved successfully');
        resolve(matchInfo);
      });

      // Request match info from GC
      this.csgoClient.requestGame(sharecode);
    });
  }

  disconnect() {
    if (this.csgoClient) {
      this.csgoClient.exit();
    }
    if (this.steamClient) {
      this.steamClient.logOff();
    }
    this.ready = false;
  }
}

// Singleton instance
let instance = null;

module.exports = {
  getInstance: () => {
    if (!instance) {
      instance = new GCClient();
    }
    return instance;
  }
};
