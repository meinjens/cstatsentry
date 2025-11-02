# Test-Driven Development Guide

## Quick Start

1. **Setup Tests**:
   ```bash
   cd backend
   pip install pytest pytest-cov pytest-asyncio httpx
   ```

2. **Run Tests**:
   ```bash
   # All tests
   make test
   # or: python -m pytest -v

   # Unit tests only (fast)
   make test-unit
   # or: python -m pytest -v -m "unit"

   # With coverage
   make test-coverage
   # or: python -m pytest -v --cov=app --cov-report=term-missing

   # TDD example (will fail until implemented)
   make test-tdd
   # or: python -m pytest -v tests/test_tdd_example.py
   ```

## TDD Workflow

### 1. Red - Write a Failing Test

```python
def test_get_player_stats_success(self, authenticated_client):
    """Test getting player stats - this will fail initially"""
    steam_id = "76561198123456789"
    response = authenticated_client.get(f"/api/v1/players/{steam_id}/stats")

    assert response.status_code == 200
    data = response.json()
    assert "total_kills" in data
```

### 2. Green - Write Minimal Code to Pass

```python
@router.get("/{steam_id}/stats")
async def get_player_stats(steam_id: str):
    return {"total_kills": 0}  # Minimal implementation
```

### 3. Refactor - Improve the Code

```python
@router.get("/{steam_id}/stats")
async def get_player_stats(
    steam_id: str,
    db: Session = Depends(get_db)
) -> PlayerStats:
    # Proper implementation with database queries
    player = get_player_by_steam_id(db, steam_id)
    if not player:
        raise HTTPException(404, "Player not found")

    stats = calculate_player_stats(db, steam_id)
    return PlayerStats(**stats)
```

## Available Test Fixtures

- `client` - Unauthenticated FastAPI test client
- `authenticated_client` - Authenticated test client with test user
- `admin_client` - Authenticated test client with admin user
- `test_user` - Regular test user
- `test_admin_user` - Admin test user
- `db_session` - Test database session
- `sample_player_data` - Sample player data
- `sample_match_data` - Sample match data

## Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_calculation():
    """Fast unit test"""
    pass

@pytest.mark.integration
def test_api_endpoint():
    """Integration test with database"""
    pass

@pytest.mark.slow
def test_external_api():
    """Slow test with external API calls"""
    pass

@pytest.mark.auth
def test_authentication():
    """Authentication-related test"""
    pass
```

## Running Specific Tests

```bash
# Run only unit tests
make test-unit
# or: python -m pytest -v -m "unit"

# Run only integration tests
make test-integration
# or: python -m pytest -v -m "integration"

# Run specific file
make test-file FILE=tests/test_players.py
# or: python -m pytest -v tests/test_players.py

# Run specific function
make test-func FUNC=test_get_player_stats
# or: python -m pytest -v -k "test_get_player_stats"

# Run without slow external API tests
pytest -m "not slow"

# Run with verbose output and coverage
make test-coverage
# or: python -m pytest -v --cov=app --cov-report=term-missing
```

## Example: Adding a New Feature

1. **Write the test first** in `tests/test_tdd_example.py`
2. **Run the test** - it should fail (Red)
3. **Implement minimal code** to make it pass (Green)
4. **Refactor** the code while keeping tests green
5. **Add more test cases** for edge cases

## Authentication in Tests

No Steam login needed! Use the provided fixtures:

```python
def test_my_endpoint(authenticated_client):
    """Test with automatic authentication"""
    response = authenticated_client.get("/api/v1/protected-endpoint")
    assert response.status_code == 200

def test_admin_only_endpoint(admin_client):
    """Test with admin authentication"""
    response = admin_client.post("/api/v1/admin-endpoint")
    assert response.status_code == 200
```

## Database Testing

Tests use SQLite in-memory database with automatic cleanup:

```python
def test_create_user(db_session):
    """Test user creation"""
    user_data = {"steam_id": "123", "steam_name": "Test"}
    user = create_user(db_session, user_data)
    assert user.steam_id == "123"
    # Database automatically cleaned up after test
```

## Mocking External Services

```python
def test_steam_api_call(monkeypatch):
    """Test with mocked Steam API"""
    async def mock_get_player_summaries(steam_ids):
        return {"response": {"players": [{"steamid": "123"}]}}

    monkeypatch.setattr(steam_api, "get_player_summaries", mock_get_player_summaries)
    # Now your test uses the mock instead of real API
```

## Tips

- **Start with failing tests** - ensures your test actually tests something
- **Keep tests focused** - one concept per test
- **Use descriptive names** - test names should explain what they verify
- **Test behavior, not implementation** - focus on what the code should do
- **Mock external dependencies** - keep tests fast and reliable
- **Use fixtures** - avoid duplicate setup code

## Running Tests in CI/CD

The test suite is configured to:
- Run all tests on every commit
- Generate coverage reports
- Fail if coverage drops below 80%
- Skip slow tests by default (run them nightly)

Happy test-driven developing! 🧪