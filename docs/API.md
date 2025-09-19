# StatSentry API Documentation

## Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

## Authentication

StatSentry uses JWT (JSON Web Tokens) for authentication with Steam OpenID.

### Headers

All authenticated requests must include:

```
Authorization: Bearer <access_token>
```

## Authentication Endpoints

### Steam Login

**GET** `/auth/steam/login`

Initiates Steam OpenID authentication flow.

**Response:**
```json
{
  "auth_url": "https://steamcommunity.com/openid/login?..."
}
```

### Steam Callback

**GET** `/auth/steam/callback`

Handles Steam OpenID callback with query parameters.

**Parameters:**
- All OpenID parameters from Steam

**Response:**
```json
{
  "steam_id": "76561198000000000",
  "steam_name": "PlayerName",
  "avatar_url": "https://steamcdn-a.akamaihd.net/...",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Refresh Token

**POST** `/auth/refresh`

Refreshes the current access token.

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Current User

**GET** `/auth/me`

Returns current authenticated user information.

**Response:**
```json
{
  "user_id": 1,
  "steam_id": "76561198000000000",
  "steam_name": "PlayerName",
  "avatar_url": "https://steamcdn-a.akamaihd.net/...",
  "last_sync": "2025-09-18T23:15:00Z",
  "sync_enabled": true,
  "created_at": "2025-09-18T20:00:00Z",
  "updated_at": "2025-09-18T23:15:00Z"
}
```

### Logout

**POST** `/auth/logout`

Logs out the current user.

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## User Endpoints

### Get Profile

**GET** `/users/me`

Returns current user profile.

**Response:** Same as `/auth/me`

### Update Profile

**PUT** `/users/me`

Updates current user profile.

**Request Body:**
```json
{
  "steam_name": "NewName",
  "sync_enabled": false
}
```

**Response:** Updated user object

## Player Endpoints

### Get Player Details

**GET** `/players/{steam_id}`

Returns detailed player information with latest analysis.

**Response:**
```json
{
  "steam_id": "76561198000000000",
  "current_name": "PlayerName",
  "previous_names": ["OldName1", "OldName2"],
  "avatar_url": "https://steamcdn-a.akamaihd.net/...",
  "profile_url": "https://steamcommunity.com/profiles/...",
  "account_created": "2015-01-01T00:00:00Z",
  "last_logoff": "2025-09-18T22:00:00Z",
  "profile_state": 1,
  "visibility_state": 3,
  "country_code": "US",
  "cs2_hours": 1500,
  "total_games_owned": 250,
  "profile_updated": "2025-09-18T23:00:00Z",
  "stats_updated": "2025-09-18T23:00:00Z",
  "created_at": "2025-09-18T20:00:00Z",
  "latest_analysis": {
    "analysis_id": 1,
    "steam_id": "76561198000000000",
    "analyzed_by": 1,
    "suspicion_score": 75,
    "flags": {
      "new_account": {
        "severity": "medium",
        "description": "Account created 25 days ago",
        "value": 25
      }
    },
    "confidence_level": 0.85,
    "analysis_version": "1.0",
    "notes": "Analysis based on 1 detection criteria",
    "analyzed_at": "2025-09-18T23:00:00Z"
  },
  "ban_info": {
    "steam_id": "76561198000000000",
    "community_banned": false,
    "vac_banned": false,
    "number_of_vac_bans": 0,
    "days_since_last_ban": 0,
    "number_of_game_bans": 0,
    "economy_ban": "none",
    "updated_at": "2025-09-18T23:00:00Z"
  }
}
```

### Get Player Analysis History

**GET** `/players/{steam_id}/analysis`

Returns analysis history for a player.

**Parameters:**
- `limit`: Number of analyses to return (default: 10, max: 100)

**Response:**
```json
[
  {
    "analysis_id": 1,
    "steam_id": "76561198000000000",
    "analyzed_by": 1,
    "suspicion_score": 75,
    "flags": {...},
    "confidence_level": 0.85,
    "analysis_version": "1.0",
    "notes": "Analysis based on 1 detection criteria",
    "analyzed_at": "2025-09-18T23:00:00Z"
  }
]
```

### Trigger Player Analysis

**POST** `/players/{steam_id}/analyze`

Triggers manual analysis for a player.

**Response:**
```json
{
  "message": "Analysis triggered for player 76561198000000000",
  "status": "queued"
}
```

### Get Suspicious Players

**GET** `/players`

Returns list of suspicious players.

**Parameters:**
- `min_suspicion_score`: Minimum suspicion score (default: 60)
- `limit`: Number of players to return (default: 50, max: 100)

**Response:** Array of player objects

## Match Endpoints

### Get Matches

**GET** `/matches`

Returns user's match history.

**Parameters:**
- `limit`: Number of matches (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "matches": [
    {
      "match_id": "CSGO-ABC123-DEF456-GHI789",
      "user_id": 1,
      "match_date": "2025-09-18T22:00:00Z",
      "map": "de_dust2",
      "score_team1": 16,
      "score_team2": 14,
      "user_team": 1,
      "sharing_code": "CSGO-ABC123-DEF456-GHI789",
      "leetify_match_id": "12345",
      "processed": true,
      "created_at": "2025-09-18T22:30:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Get Match Details

**GET** `/matches/{match_id}`

Returns detailed match information.

**Response:** Match object with additional player details

### Trigger Match Sync

**POST** `/matches/sync`

Triggers manual match synchronization.

**Response:**
```json
{
  "message": "Match synchronization started",
  "user_id": 1,
  "status": "queued"
}
```

### Get Sync Status

**GET** `/matches/sync/status`

Returns current synchronization status.

**Response:**
```json
{
  "status": "idle",
  "last_sync": "2025-09-18T23:00:00Z",
  "sync_enabled": true
}
```

## Dashboard Endpoints

### Get Dashboard Summary

**GET** `/dashboard/summary`

Returns dashboard overview statistics.

**Response:**
```json
{
  "total_matches": 150,
  "total_players_analyzed": 450,
  "suspicious_players": 25,
  "high_risk_players": 5,
  "new_detections_today": 3,
  "last_sync": "2025-09-18T23:00:00Z"
}
```

### Get Recent Activity

**GET** `/dashboard/recent`

Returns recent suspicious activities.

**Response:**
```json
{
  "recent_analyses": [...],
  "new_flags": [...],
  "updated_players": [...]
}
```

### Get Statistics

**GET** `/dashboard/statistics`

Returns detailed user statistics and trends.

**Response:**
```json
{
  "matches_by_month": [...],
  "suspicion_score_distribution": {...},
  "detection_trends": [...],
  "most_common_flags": [...]
}
```

## System Endpoints

### Health Check

**GET** `/health`

Returns system health status.

**Response:**
```json
{
  "status": "healthy"
}
```

### API Version

**GET** `/`

Returns API information.

**Response:**
```json
{
  "message": "StatSentry API",
  "version": "1.0.0"
}
```

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access forbidden"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authentication endpoints:** 10 requests per minute
- **General endpoints:** 100 requests per minute
- **Analysis endpoints:** 20 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Requests allowed per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Window reset time

## WebSocket

Real-time updates are available via WebSocket:

**Endpoint:** `/ws/updates`

**Authentication:** Include JWT token as query parameter

**Events:**
- `player_analysis_complete`: New analysis results
- `match_sync_update`: Match synchronization progress
- `suspicious_player_detected`: New suspicious player found