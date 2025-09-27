# Integration Testing with Mock Services

## Overview

This setup provides a complete Docker-based integration testing environment with mock external services, eliminating the need for real Steam API calls during development and testing.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Tests    │────│  CStatSentry    │────│  Mock Steam API │
│                 │    │     API         │    │   (Flask)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Test Database │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

## Quick Start

### 1. Start Mock Services

```bash
# Start all mock services
make start-mock-services
# or: docker-compose -f docker-compose.test.yml up -d mock-steam-api test-db test-redis

# Verify services are running
curl http://localhost:5001/health
```

### 2. Run Integration Tests

```bash
# Run integration tests with mock services
make test-with-mocks
# or: cd backend && MOCK_STEAM_API_URL=http://localhost:5001 DATABASE_URL=postgresql://test_user:test_password@localhost:5433/test_statsentry python -m pytest tests/test_integration_steam_mock.py -v -m integration

# Or run full Docker-based integration tests
make test-integration-docker
# or: docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### 3. Explore Mock Services

- **Mock Steam API**: http://localhost:5001
- **Test Database**: localhost:5433
- **Test Redis**: localhost:6380

## Mock Steam API Features

### Available Endpoints

- `GET /health` - Health check
- `GET /ISteamUser/GetPlayerSummaries/v0002/` - Player profile data
- `GET /ISteamUser/GetPlayerBans/v1/` - Player ban information
- `GET /ISteamUserStats/GetUserStatsForGame/v0002/` - Player game stats
- `GET /openid/login` - Steam OpenID login simulation

### Admin Endpoints

- `GET /admin/users` - List all mock users
- `POST /admin/users` - Create new mock user
- `DELETE /admin/users/{steam_id}` - Delete mock user

### Pre-configured Test Users

| Steam ID | Username | Purpose |
|----------|----------|---------|
| 76561198123456789 | TestPlayer | Standard test user |
| 76561198999999999 | AdminUser | Admin test user |
| 76561197960287930 | DevUser | Development user |

## Usage Examples

### Testing Steam Authentication

```python
@pytest.mark.integration
async def test_steam_auth_flow(client, mock_steam_config):
    # Get login URL
    response = client.get("/api/v1/auth/steam/login")
    auth_url = response.json()["auth_url"]

    # Simulate Steam callback
    callback_params = {
        "openid.mode": "id_res",
        "openid.claimed_id": "https://steamcommunity.com/openid/id/76561198123456789",
        # ... other OpenID parameters
    }

    response = client.get("/api/v1/auth/steam/callback", params=callback_params)
    assert response.status_code == 200

    token = response.json()["access_token"]
    # Use token for authenticated requests...
```

### Testing Steam API Integration

```python
@pytest.mark.integration
async def test_player_data_retrieval(mock_steam_service_health):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:5001/ISteamUser/GetPlayerSummaries/v0002/",
            params={
                "steamids": "76561198123456789",
                "key": "test-steam-api-key"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"]["players"][0]["personaname"] == "TestPlayer"
```

### Creating Custom Test Data

```python
async def test_with_custom_user():
    async with httpx.AsyncClient() as client:
        # Create custom test user
        new_user = {
            "steamid": "76561198888777666",
            "personaname": "CustomTestUser",
            "avatar": "https://example.com/custom_avatar.jpg"
        }

        response = await client.post(
            "http://localhost:5001/admin/users",
            json=new_user
        )
        assert response.status_code == 200

        # Now use this user in your tests...

        # Cleanup
        await client.delete("http://localhost:5001/admin/users/76561198888777666")
```

## Development Workflow

### 1. Write Failing Tests First

```bash
# Write your integration test
vim backend/tests/test_my_new_feature_integration.py

# Run it (should fail)
make test-with-mocks
# or: cd backend && python -m pytest tests/test_my_new_feature_integration.py -v
```

### 2. Implement Feature

```bash
# Implement your feature
vim backend/app/api/api_v1/endpoints/my_endpoint.py

# Test again
make test-with-mocks
# or: cd backend && python -m pytest tests/test_my_new_feature_integration.py -v
```

### 3. Iterate Until Green

```bash
# Keep running tests as you develop
make test-with-mocks
# or: cd backend && python -m pytest tests/test_my_new_feature_integration.py -v

# Or run in watch mode (if you have pytest-watch)
cd backend && ptw tests/test_my_new_feature_integration.py
```

## Configuration

### Environment Variables

```bash
# Mock service URLs (automatically set by make commands)
MOCK_STEAM_API_URL=http://localhost:5001
STEAM_API_BASE_URL=http://localhost:5001
STEAM_OPENID_URL=http://localhost:5001/openid

# Test database
DATABASE_URL=postgresql://test_user:test_password@localhost:5433/test_statsentry

# Test Redis
REDIS_URL=redis://localhost:6380/0
```

### Docker Compose Services

The `docker-compose.test.yml` includes:

- **test-db**: PostgreSQL database for testing
- **test-redis**: Redis instance for testing
- **mock-steam-api**: Flask-based Steam API mock

## Debugging

### View Mock Service Logs

```bash
docker-compose -f docker-compose.test.yml logs mock-steam-api
```

### Access Mock Service Directly

```bash
# Check health
curl http://localhost:5001/health

# View available test users
curl http://localhost:5001/admin/users

# Test Steam API endpoint
curl "http://localhost:5001/ISteamUser/GetPlayerSummaries/v0002/?steamids=76561198123456789&key=test-key"
```

### Connect to Test Database

```bash
psql postgresql://test_user:test_password@localhost:5433/test_statsentry
```

## Best Practices

1. **Use Fixtures**: Create reusable test fixtures for common scenarios
2. **Mark Tests**: Use `@pytest.mark.integration` for integration tests
3. **Mock External Calls**: Even in integration tests, mock calls to real external services
4. **Clean Up**: Use fixtures that clean up test data automatically
5. **Health Checks**: Always verify mock services are healthy before tests
6. **Realistic Data**: Use realistic test data that matches real Steam API responses

## Troubleshooting

### Mock Service Won't Start

```bash
# Check if ports are in use
netstat -tulpn | grep :5001

# Force rebuild
docker-compose -f docker-compose.test.yml up --build --force-recreate
```

### Tests Can't Connect to Mock Service

```bash
# Verify service is running
make start-mock-services
# or: docker-compose -f docker-compose.test.yml up -d
curl http://localhost:5001/health

# Check Docker networks
docker-compose -f docker-compose.test.yml ps
```

### Database Connection Issues

```bash
# Check if test database is running
docker-compose -f docker-compose.test.yml ps test-db

# Test connection
psql postgresql://test_user:test_password@localhost:5433/test_statsentry -c "SELECT 1;"
```

This setup gives you:
- ✅ **No external dependencies** - everything runs locally
- ✅ **Fast tests** - no network calls to real APIs
- ✅ **Deterministic data** - consistent test results
- ✅ **Full control** - customize test scenarios easily
- ✅ **Real integration** - tests actual HTTP flows and database operations

Happy integration testing! 🐳🧪