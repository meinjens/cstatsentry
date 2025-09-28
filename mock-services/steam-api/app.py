#!/usr/bin/env python3
"""
Mock Steam API Service for Integration Testing

This service mimics the Steam Web API endpoints used by CStatSentry
for testing purposes without hitting the real Steam API.
"""

import time
from datetime import datetime

from flask import Flask, request, jsonify

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

# Mock Leetify data
MOCK_MATCHES = {
    "76561198123456789": [
        {
            "matchId": "3-match-2025-09-28-001",
            "gameType": "competitive",
            "map": "de_dust2",
            "startTime": 1727512800000,  # 2025-09-28 12:00:00 UTC
            "endTime": 1727515500000,    # 2025-09-28 12:45:00 UTC
            "rounds": 30,
            "teamAScore": 16,
            "teamBScore": 14,
            "myTeam": "A",
            "result": "win",
            "players": [
                {
                    "steamId": "76561198123456789",
                    "name": "TestPlayer",
                    "team": "A",
                    "kills": 25,
                    "deaths": 18,
                    "assists": 7,
                    "adr": 82.5,
                    "rating": 1.15,
                    "headshots": 12,
                    "mvps": 3
                },
                {
                    "steamId": "76561198999999998",
                    "name": "Teammate1",
                    "team": "A",
                    "kills": 20,
                    "deaths": 20,
                    "assists": 5,
                    "adr": 75.2,
                    "rating": 1.02,
                    "headshots": 8,
                    "mvps": 2
                },
                {
                    "steamId": "76561198999999997",
                    "name": "Teammate2",
                    "team": "A",
                    "kills": 18,
                    "deaths": 22,
                    "assists": 8,
                    "adr": 68.9,
                    "rating": 0.95,
                    "headshots": 6,
                    "mvps": 1
                },
                {
                    "steamId": "76561198999999996",
                    "name": "Teammate3",
                    "team": "A",
                    "kills": 22,
                    "deaths": 19,
                    "assists": 4,
                    "adr": 79.1,
                    "rating": 1.08,
                    "headshots": 9,
                    "mvps": 4
                },
                {
                    "steamId": "76561198999999995",
                    "name": "Teammate4",
                    "team": "A",
                    "kills": 19,
                    "deaths": 21,
                    "assists": 6,
                    "adr": 71.8,
                    "rating": 0.98,
                    "headshots": 7,
                    "mvps": 1
                },
                {
                    "steamId": "76561198999999994",
                    "name": "Enemy1",
                    "team": "B",
                    "kills": 23,
                    "deaths": 20,
                    "assists": 3,
                    "adr": 84.2,
                    "rating": 1.12,
                    "headshots": 11,
                    "mvps": 2
                },
                {
                    "steamId": "76561198999999993",
                    "name": "Enemy2",
                    "team": "B",
                    "kills": 18,
                    "deaths": 21,
                    "assists": 7,
                    "adr": 69.5,
                    "rating": 0.91,
                    "headshots": 5,
                    "mvps": 1
                },
                {
                    "steamId": "76561198999999992",
                    "name": "Enemy3",
                    "team": "B",
                    "kills": 17,
                    "deaths": 22,
                    "assists": 5,
                    "adr": 65.3,
                    "rating": 0.88,
                    "headshots": 4,
                    "mvps": 0
                },
                {
                    "steamId": "76561198999999991",
                    "name": "Enemy4",
                    "team": "B",
                    "kills": 21,
                    "deaths": 21,
                    "assists": 4,
                    "adr": 76.8,
                    "rating": 1.01,
                    "headshots": 8,
                    "mvps": 3
                },
                {
                    "steamId": "76561198999999990",
                    "name": "Enemy5",
                    "team": "B",
                    "kills": 21,
                    "deaths": 20,
                    "assists": 6,
                    "adr": 78.9,
                    "rating": 1.05,
                    "headshots": 9,
                    "mvps": 2
                }
            ]
        },
        {
            "matchId": "3-match-2025-09-27-001",
            "gameType": "competitive",
            "map": "de_mirage",
            "startTime": 1727426400000,  # 2025-09-27 12:00:00 UTC
            "endTime": 1727429100000,    # 2025-09-27 12:45:00 UTC
            "rounds": 25,
            "teamAScore": 13,
            "teamBScore": 16,
            "myTeam": "A",
            "result": "loss",
            "players": [
                {
                    "steamId": "76561198123456789",
                    "name": "TestPlayer",
                    "team": "A",
                    "kills": 18,
                    "deaths": 22,
                    "assists": 5,
                    "adr": 69.2,
                    "rating": 0.89,
                    "headshots": 7,
                    "mvps": 1
                }
                # ... more players would be here
            ]
        }
    ]
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

        <h2>🎯 Leetify API Endpoints</h2>

        <div class="endpoint">
            <span class="method">POST</span> /api/auth/token - Get authentication token
        </div>

        <div class="endpoint">
            <span class="method">GET</span> /api/profile/{steam_id}/games - Get recent games for player
        </div>

        <div class="endpoint">
            <span class="method">GET</span> /api/profile/{steam_id}/recent-games - Get latest games (simplified)
        </div>

        <div class="endpoint">
            <span class="method">GET</span> /api/games/{match_id} - Get detailed match data
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

    # If this is a POST request with verification data, handle verification
    if request.method == 'POST':
        return openid_verify()

    # GET request - show login page
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
    # Check if this is a verification request
    mode = request.form.get('openid.mode') or request.values.get('openid.mode')

    if mode == 'check_authentication':
        # Mock successful verification response
        return "ns:http://specs.openid.net/auth/2.0\nis_valid:true\n"

    # For other modes, return an error
    return "ns:http://specs.openid.net/auth/2.0\nis_valid:false\n"


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


# Leetify API Mock Endpoints
@app.route('/api/profile/<steam_id>/games', methods=['GET'])
def leetify_get_games(steam_id):
    """Mock Leetify API - Get recent games for a player"""
    # Validate authentication (simple mock)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Invalid authentication"}), 401

    # Get query parameters
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    if steam_id not in MOCK_MATCHES:
        return jsonify({
            "games": [],
            "hasMore": False,
            "total": 0
        })

    all_matches = MOCK_MATCHES[steam_id]

    # Apply pagination
    start_idx = offset
    end_idx = start_idx + limit
    matches_page = all_matches[start_idx:end_idx]

    return jsonify({
        "games": matches_page,
        "hasMore": end_idx < len(all_matches),
        "total": len(all_matches)
    })


@app.route('/api/games/<match_id>', methods=['GET'])
def leetify_get_game_details(match_id):
    """Mock Leetify API - Get detailed game data"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Invalid authentication"}), 401

    # Find match across all users
    for steam_id, matches in MOCK_MATCHES.items():
        for match in matches:
            if match['matchId'] == match_id:
                return jsonify(match)

    return jsonify({"error": "Match not found"}), 404


@app.route('/api/profile/<steam_id>/recent-games', methods=['GET'])
def leetify_get_recent_games(steam_id):
    """Mock Leetify API - Get most recent games (simplified)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Invalid authentication"}), 401

    if steam_id not in MOCK_MATCHES:
        return jsonify([])

    # Return last 5 matches by default
    recent_matches = MOCK_MATCHES[steam_id][:5]
    return jsonify(recent_matches)


@app.route('/api/auth/token', methods=['POST'])
def leetify_auth():
    """Mock Leetify API - Authentication endpoint"""
    data = request.get_json()

    # Simple mock authentication
    if data and data.get('steam_id'):
        return jsonify({
            "access_token": f"mock_token_{data['steam_id']}_{int(time.time())}",
            "token_type": "Bearer",
            "expires_in": 3600
        })

    return jsonify({"error": "Invalid credentials"}), 401


# Additional Mock Data Generation
def generate_random_match(steam_id, match_number=1):
    """Generate a random match for testing"""
    import random

    maps = ["de_dust2", "de_mirage", "de_inferno", "de_cache", "de_overpass", "de_train", "de_nuke"]

    base_time = int(time.time()) - (match_number * 86400)  # One day apart

    return {
        "matchId": f"3-match-{datetime.fromtimestamp(base_time).strftime('%Y-%m-%d')}-{match_number:03d}",
        "gameType": "competitive",
        "map": random.choice(maps),
        "startTime": base_time * 1000,
        "endTime": (base_time + random.randint(1800, 3600)) * 1000,
        "rounds": random.randint(16, 30),
        "teamAScore": random.randint(13, 16),
        "teamBScore": random.randint(13, 16),
        "myTeam": random.choice(["A", "B"]),
        "result": random.choice(["win", "loss", "tie"]),
        "players": [
            {
                "steamId": steam_id,
                "name": MOCK_USERS.get(steam_id, {}).get("personaname", "Unknown"),
                "team": "A",
                "kills": random.randint(10, 30),
                "deaths": random.randint(10, 25),
                "assists": random.randint(0, 10),
                "adr": round(random.uniform(50.0, 100.0), 1),
                "rating": round(random.uniform(0.5, 1.8), 2),
                "headshots": random.randint(3, 15),
                "mvps": random.randint(0, 5)
            }
            # Simplified - would have more players in real implementation
        ]
    }


@app.route('/admin/matches/generate/<steam_id>', methods=['POST'])
def admin_generate_matches(steam_id):
    """Admin endpoint to generate random matches for testing"""
    count = int(request.args.get('count', 5))

    if steam_id not in MOCK_MATCHES:
        MOCK_MATCHES[steam_id] = []

    new_matches = []
    for i in range(count):
        match = generate_random_match(steam_id, len(MOCK_MATCHES[steam_id]) + i + 1)
        new_matches.append(match)

    MOCK_MATCHES[steam_id].extend(new_matches)

    return jsonify({
        "message": f"Generated {count} matches for {steam_id}",
        "total_matches": len(MOCK_MATCHES[steam_id])
    })


if __name__ == '__main__':
    print("🎮 Mock Steam API + Leetify Service")
    print("📍 Running on http://localhost:5001")
    print("🔗 Steam OpenID: http://localhost:5001/openid/login")
    print("🎯 Leetify API: http://localhost:5001/api/")
    print("❤️  Health: http://localhost:5001/health")
    app.run(host='0.0.0.0', port=5001, debug=True)