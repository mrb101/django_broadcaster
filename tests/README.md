# Django Dispatch Tests

This directory contains tests for the Django Dispatch package.

## Running Tests

To run the tests, use pytest:

```bash
pytest
```

Or to run with coverage:

```bash
pytest --cov=django_broadcaster
```

## Test Structure

The tests are organized by module:

- `test_events.py`: Tests for the CloudEvent class
- `test_models.py`: Tests for the OutboxEvent model
- `test_backends.py`: Tests for the publisher backends
- `test_publishers.py`: Tests for the OutboxPublisher class
- `test_registry.py`: Tests for the EventHandlerRegistry
- `test_signals.py`: Tests for the signal handlers
- `test_admin.py`: Tests for the Django admin interface
- `test_apps.py`: Tests for the Django app configuration

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `outbox_event`: Creates a test OutboxEvent instance
- `cloud_event`: Creates a test CloudEvent instance
- `mock_redis`: Mocks the Redis client for testing

## Django Configuration

The tests use an in-memory SQLite database and a minimal Django configuration defined in `conftest.py`.
