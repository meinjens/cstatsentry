#!/usr/bin/env python3
"""
Mock Steam API Service for Integration Testing

This service mimics the Steam Web API endpoints used by CStatSentry
for testing purposes without hitting the real Steam API.
"""

import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)

# Mock data store
MOCK_USERS = {
    "76561198123456789": {
        "steamid": "76561198123456789",
        "personaname": "TestPlayer",
        "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/test_small.jpg",
        "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/test_medium.jpg",
        "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/test_full.jpg",
        "personastate": 1,
        "communityvisibilitystate": 3,
        "profilestate": 1,
        "realname": "Test Player",
        "primaryclanid": "103582791429521408",
        "timecreated": 1234567890,
        "personastateflags": 0,
        "loccountrycode": "US",
        "locstatecode": "CA",
        "loccityid": 5392171
    },
    "76561198999999999": {
        "steamid": "76561198999999999",
        "personaname": "AdminUser",
        "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/admin.jpg",
        "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/admin_medium.jpg",
        "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/admin_full.jpg",
        "personastate": 1,
        "communityvisibilitystate": 3,
        "profilestate": 1,
        "realname": "Admin User",
        "timecreated": 1234567890,
        "personastateflags": 0
    },
    "76561197960287930": {
        "steamid": "76561197960287930",
        "personaname": "DevUser",
        "avatar": "https://via.placeholder.com/32x32.png?text=Dev",
        "avatarmedium": "https://via.placeholder.com/64x64.png?text=Dev",
        "avatarfull": "https://via.placeholder.com/184x184.png?text=Dev",
        "personastate": 1,
        "communityvisibilitystate": 3,
        "profilestate": 1,
        "realname": "Development User",
        "timecreated": 1234567890,
        "personastateflags": 0
    }
}

MOCK_BANS = {
    "76561198123456789": {
        "SteamId": "76561198123456789",
        "CommunityBanned": False,
        "VACBanned": False,
        "NumberOfVACBans": 0,
        "DaysSinceLastBan": 0,
        "NumberOfGameBans": 0,
        "EconomyBan": "none"
    }
}


@app.route('/')
def index():
    """Mock Steam API landing page"""
    return '''
    <html>
    <head>
        <title>Mock Steam API Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1b2838; color: #c7d5e0; }
            h1 { color: #67c1f5; }
            h2 { color: #67c1f5; margin-top: 30px; }
            .endpoint { background: #2a475e; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { background: #4c6a83; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
            a { color: #67c1f5; text-decoration: none; }
            a:hover { text-decoration: underline; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #4c6a83; padding: 8px; text-align: left; }
            th { background: #2a475e; }
            .health { color: #90ba3c; }
        </style>
    </head>
    <body>
        <h1>🎮 Mock Steam API Service</h1>
        <p class="health">✅ Service is running and healthy</p>

        <h2>🔌 Available Endpoints</h2>

        <div class="endpoint">
            <span class="method">GET</span> <a href="/health">/health</a> - Health check
        </div>

        <div class="endpoint">
            <span class="method">GET</span> <a href="/ISteamUser/GetPlayerSummaries/v0002/?steamids=76561198123456789&key=test-key">/ISteamUser/GetPlayerSummaries/v0002/</a> - Player summaries
        </div>

        <div class="endpoint">
            <span class="method">GET</span> <a href="/ISteamUser/GetPlayerBans/v1/?steamids=76561198123456789&key=test-key">/ISteamUser/GetPlayerBans/v1/</a> - Player bans
        </div>

        <div class="endpoint">
            <span class="method">GET</span> <a href="/ISteamUserStats/GetUserStatsForGame/v0002/?steamid=76561198123456789&appid=730&key=test-key">/ISteamUserStats/GetUserStatsForGame/v0002/</a> - Player game stats
        </div>

        <div class="endpoint">
            <span class="method">GET</span> <a href="/openid/login">/openid/login</a> - Steam OpenID login simulation
        </div>

        <h2>👥 Pre-configured Test Users</h2>
        <table>
            <tr><th>Steam ID</th><th>Username</th><th>Purpose</th></tr>
            <tr><td>76561198123456789</td><td>TestPlayer</td><td>Standard test user</td></tr>
            <tr><td>76561198999999999</td><td>AdminUser</td><td>Admin test user</td></tr>
            <tr><td>76561197960287930</td><td>DevUser</td><td>Development user</td></tr>
        </table>

        <h2>🛠 Admin Endpoints</h2>
        <div class="endpoint">
            <span class="method">GET</span> <a href="/admin/users">/admin/users</a> - List all users
        </div>
        <div class="endpoint">
            <span class="method">POST</span> /admin/users - Create new user
        </div>
        <div class="endpoint">
            <span class="method">DELETE</span> /admin/users/{steam_id} - Delete user
        </div>

        <h2>🧪 Quick Tests</h2>
        <p>Try these endpoints to test the mock service:</p>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/admin/users">List Users</a></li>
            <li><a href="/ISteamUser/GetPlayerSummaries/v0002/?steamids=76561198123456789&key=test-key">Get TestPlayer Profile</a></li>
            <li><a href="/openid/login">Steam Login Simulation</a></li>
        </ul>

        <h2>📝 Usage</h2>
        <p>This mock service simulates the Steam Web API for testing CStatSentry without hitting the real Steam servers.</p>
        <p>Use API key "test-key" for all requests.</p>

        <hr style="margin: 40px 0; border-color: #4c6a83;">
        <p style="text-align: center; color: #8091a2;">
            🐳 Running in Docker | 🔧 Built for Integration Testing
        </p>
    </body>
    </html>
    '''


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "mock-steam-api"})


@app.route('/ISteamUser/GetPlayerSummaries/v0002/')
def get_player_summaries():
    """Mock Steam API GetPlayerSummaries endpoint"""
    steamids = request.args.get('steamids', '')
    key = request.args.get('key', '')

    # Validate API key (for testing)
    if not key:
        return jsonify({"error": "Missing API key"}), 400

    if key == "invalid-key":
        return jsonify({"error": "Invalid API key"}), 401

    # Parse steam IDs
    steam_ids = [sid.strip() for sid in steamids.split(',') if sid.strip()]

    if not steam_ids:
        return jsonify({"error": "Missing steamids parameter"}), 400

    # Build response
    players = []
    for steam_id in steam_ids:
        if steam_id in MOCK_USERS:
            players.append(MOCK_USERS[steam_id])

    response = {
        "response": {
            "players": players
        }
    }

    return jsonify(response)


@app.route('/ISteamUser/GetPlayerBans/v1/')
def get_player_bans():
    """Mock Steam API GetPlayerBans endpoint"""
    steamids = request.args.get('steamids', '')
    key = request.args.get('key', '')

    if not key:
        return jsonify({"error": "Missing API key"}), 400

    steam_ids = [sid.strip() for sid in steamids.split(',') if sid.strip()]

    players = []
    for steam_id in steam_ids:
        if steam_id in MOCK_BANS:
            players.append(MOCK_BANS[steam_id])
        else:
            # Default ban info for unknown players
            players.append({
                "SteamId": steam_id,
                "CommunityBanned": False,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none"
            })

    return jsonify({"players": players})


@app.route('/ISteamUserStats/GetUserStatsForGame/v0002/')
def get_user_stats_for_game():
    """Mock Steam API GetUserStatsForGame endpoint"""
    steamid = request.args.get('steamid', '')
    appid = request.args.get('appid', '')
    key = request.args.get('key', '')

    if not all([steamid, appid, key]):
        return jsonify({"error": "Missing required parameters"}), 400

    if steamid not in MOCK_USERS:
        return jsonify({"error": "Player not found"}), 404

    # Mock CS2/CSGO stats
    if appid in ["730", "440"]:  # CS2 or TF2
        stats = {
            "playerstats": {
                "steamID": steamid,
                "gameName": "ValveTestApp260",
                "stats": [
                    {"name": "total_kills", "value": 1337},
                    {"name": "total_deaths", "value": 1000},
                    {"name": "total_time_played", "value": 123456},
                    {"name": "total_planted_bombs", "value": 42},
                    {"name": "total_defused_bombs", "value": 24},
                    {"name": "total_wins", "value": 150},
                    {"name": "total_damage_done", "value": 150000},
                    {"name": "total_money_earned", "value": 500000},
                    {"name": "total_kills_knife", "value": 15},
                    {"name": "total_kills_hegrenade", "value": 25},
                    {"name": "total_kills_headshot", "value": 400},
                    {"name": "total_shots_hit", "value": 2500},
                    {"name": "total_shots_fired", "value": 10000}
                ],
                "achievements": []
            }
        }
        return jsonify(stats)

    return jsonify({"error": "Game not found"}), 404


# OpenID endpoints for Steam authentication
@app.route('/openid/login', methods=['GET', 'POST'])
def openid_login():
    """Mock Steam OpenID login endpoint"""
    return_to = request.args.get('openid.return_to', 'http://localhost:3000/auth/steam/callback')

    # Simulate OpenID redirect with test user
    test_steam_id = "76561198123456789"

    # Build callback URL with OpenID parameters
    params = {
        'openid.mode': 'id_res',
        'openid.claimed_id': f'https://steamcommunity.com/openid/id/{test_steam_id}',
        'openid.identity': f'https://steamcommunity.com/openid/id/{test_steam_id}',
        'openid.return_to': return_to,
        'openid.response_nonce': f'{datetime.utcnow().isoformat()}Z{int(time.time())}',
        'openid.assoc_handle': 'test_handle_123',
        'openid.signed': 'signed,mode,identity,return_to,response_nonce,assoc_handle',
        'openid.sig': 'test_signature_valid'
    }

    # Build redirect URL
    separator = '&' if '?' in return_to else '?'
    param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
    redirect_url = f"{return_to}{separator}{param_string}"

    return f'''
    <html>
    <head><title>Mock Steam Login</title></head>
    <body>
        <h2>Mock Steam Login</h2>
        <p>This is a mock Steam login for testing.</p>
        <p>Click the button to simulate successful login with test user.</p>
        <a href="{redirect_url}" style="
            background: #1b2838;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 3px;
            display: inline-block;
            margin: 10px 0;
        ">Sign in through Steam (Test User)</a>

        <h3>Available Test Users:</h3>
        <ul>
            <li><strong>76561198123456789</strong> - TestPlayer (Normal User)</li>
            <li><strong>76561198999999999</strong> - AdminUser (Admin)</li>
            <li><strong>76561197960287930</strong> - DevUser (Development)</li>
        </ul>

        <h3>Test Endpoints:</h3>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/ISteamUser/GetPlayerSummaries/v0002/?steamids=76561198123456789&key=test-key">Player Summaries</a></li>
            <li><a href="/ISteamUser/GetPlayerBans/v1/?steamids=76561198123456789&key=test-key">Player Bans</a></li>
        </ul>
    </body>
    </html>
    '''


@app.route('/openid', methods=['POST'])
def openid_verify():
    """Mock OpenID verification endpoint"""
    # Always return successful verification for testing
    return "is_valid:true\n"


@app.route('/openid/id/<steam_id>')
def openid_identity(steam_id):
    """Mock OpenID identity endpoint"""
    if steam_id in MOCK_USERS:
        return f'''
        <html>
        <head><title>Steam Community :: {MOCK_USERS[steam_id]["personaname"]}</title></head>
        <body>
            <h1>{MOCK_USERS[steam_id]["personaname"]}</h1>
            <p>Steam ID: {steam_id}</p>
            <p>This is a mock Steam profile page for testing.</p>
        </body>
        </html>
        '''
    return "Profile not found", 404


# Admin endpoints for test management
@app.route('/admin/users', methods=['GET'])
def admin_list_users():
    """List all mock users"""
    return jsonify({"users": list(MOCK_USERS.keys())})


@app.route('/admin/users', methods=['POST'])
def admin_create_user():
    """Create a new mock user"""
    data = request.get_json()
    steam_id = data.get('steamid')

    if not steam_id:
        return jsonify({"error": "steamid required"}), 400

    MOCK_USERS[steam_id] = {
        "steamid": steam_id,
        "personaname": data.get('personaname', f'TestUser{steam_id[-4:]}'),
        "avatar": data.get('avatar', 'https://via.placeholder.com/32x32.png'),
        "avatarmedium": data.get('avatarmedium', 'https://via.placeholder.com/64x64.png'),
        "avatarfull": data.get('avatarfull', 'https://via.placeholder.com/184x184.png'),
        "personastate": data.get('personastate', 1),
        "communityvisibilitystate": data.get('communityvisibilitystate', 3),
        "profilestate": data.get('profilestate', 1),
        "timecreated": data.get('timecreated', int(time.time())),
        "personastateflags": data.get('personastateflags', 0)
    }

    return jsonify({"message": "User created", "steamid": steam_id})


@app.route('/admin/users/<steam_id>', methods=['DELETE'])
def admin_delete_user(steam_id):
    """Delete a mock user"""
    if steam_id in MOCK_USERS:
        del MOCK_USERS[steam_id]
        return jsonify({"message": "User deleted"})
    return jsonify({"error": "User not found"}), 404


if __name__ == '__main__':
    print("🎮 Mock Steam API Service")
    print("📍 Running on http://localhost:5001")
    print("🔗 OpenID: http://localhost:5001/openid/login")
    print("❤️  Health: http://localhost:5001/health")
    app.run(host='0.0.0.0', port=5001, debug=True)