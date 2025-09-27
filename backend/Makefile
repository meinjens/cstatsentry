.PHONY: test test-unit test-integration test-auth test-api test-coverage test-watch test-debug help

# Default target
help:
	@echo "Available test commands:"
	@echo ""
	@echo "  test                 - Run all tests"
	@echo "  test-unit           - Run only unit tests"
	@echo "  test-integration    - Run only integration tests"
	@echo "  test-auth           - Run only authentication tests"
	@echo "  test-api            - Run only API endpoint tests"
	@echo "  test-coverage       - Run tests with coverage report"
	@echo "  test-watch          - Run tests in watch mode"
	@echo "  test-debug          - Run tests with debug output"
	@echo "  test-fast           - Run tests without coverage (fastest)"
	@echo "  test-slow           - Run all tests including slow external API tests"
	@echo ""
	@echo "TDD Examples:"
	@echo "  test-tdd            - Run the TDD example tests (will fail initially)"
	@echo "  test-file FILE=path - Run specific test file"
	@echo "  test-func FUNC=name - Run specific test function"

# Run all tests
test:
	cd backend && python -m pytest -v

# Run only unit tests (fast)
test-unit:
	cd backend && python -m pytest -v -m "unit"

# Run only integration tests
test-integration:
	cd backend && python -m pytest -v -m "integration"

# Run authentication-related tests
test-auth:
	cd backend && python -m pytest -v -m "auth" tests/test_auth.py

# Run API endpoint tests
test-api:
	cd backend && python -m pytest -v -m "api"

# Run tests with coverage
test-coverage:
	cd backend && python -m pytest -v --cov=app --cov-report=term-missing --cov-report=html

# Run tests in watch mode (requires pytest-watch)
test-watch:
	cd backend && ptw -- -v

# Run tests with debug output
test-debug:
	cd backend && python -m pytest -v -s --tb=long

# Run tests without coverage (fastest)
test-fast:
	cd backend && python -m pytest -v --disable-warnings --tb=short

# Run all tests including slow ones
test-slow:
	cd backend && python -m pytest -v -m "slow"

# Run TDD example tests (these will fail until features are implemented)
test-tdd:
	cd backend && python -m pytest -v tests/test_tdd_example.py

# Run specific test file
test-file:
	cd backend && python -m pytest -v $(FILE)

# Run specific test function
test-func:
	cd backend && python -m pytest -v -k "$(FUNC)"

# Install test dependencies
install-test-deps:
	cd backend && pip install pytest pytest-cov pytest-watch pytest-asyncio httpx

# Clean test artifacts
clean-test:
	cd backend && rm -rf .pytest_cache htmlcov .coverage test.db

# Docker-based integration tests
test-integration-docker:
	docker-compose -f docker-compose.test.yml up --build -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	docker-compose -f docker-compose.test.yml exec -T mock-steam-api curl -f http://localhost:5001/health || echo "Mock service not ready"
	cd backend && MOCK_STEAM_API_URL=http://localhost:5001 python -m pytest tests/test_integration_steam_mock.py -v
	docker-compose -f docker-compose.test.yml down

# Start mock services for development
start-mock-services:
	docker-compose -f docker-compose.test.yml up -d mock-steam-api test-db test-redis
	@echo "Mock services started:"
	@echo "  Mock Steam API: http://localhost:5001"
	@echo "  Test Database: localhost:5433"
	@echo "  Test Redis: localhost:6380"

# Stop mock services
stop-mock-services:
	docker-compose -f docker-compose.test.yml down

# Test with mock services running
test-with-mocks:
	@echo "Testing with mock services..."
	cd backend && MOCK_STEAM_API_URL=http://localhost:5001 DATABASE_URL=postgresql://test_user:test_password@localhost:5433/test_statsentry python -m pytest tests/test_integration_steam_mock.py -v -m integration