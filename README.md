# Django Outbox

[![PyPI version](https://badge.fury.io/py/django-outbox.svg)](https://badge.fury.io/py/django-outbox)
[![Python versions](https://img.shields.io/pypi/pyversions/django-outbox.svg)](https://pypi.org/project/django-outbox/)
[![Django versions](https://img.shields.io/pypi/djversions/django-outbox.svg)](https://pypi.org/project/django-outbox/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/yourusername/django-outbox/workflows/CI/badge.svg)](https://github.com/yourusername/django-outbox/actions)
[![Coverage](https://codecov.io/gh/yourusername/django-outbox/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/django-outbox)

A Django app that implements the transactional outbox pattern with CloudEvents support, enabling reliable event publishing in distributed systems.

## Features

- 🔄 **Transactional Outbox Pattern**: Ensures events are published reliably
- ☁️ **CloudEvents Compatible**: Follows CloudEvents specification
- 🔌 **Multiple Backends**: Redis Streams, Kafka, NATS support
- 🔁 **Retry Logic**: Exponential backoff with configurable retries
- 🔑 **Idempotency**: Prevents duplicate event processing
- 📊 **Monitoring**: Built-in metrics and health checks
- 🎯 **Event Handlers**: Local event processing framework
- 🔧 **Admin Interface**: Django admin integration

## Quick Start

### Installation

```bash
# Using pip
pip install django-dispatch

# Using uv
uv add django-dispatch
```

## Configuration
Add to your Django settings:

```python
INSTALLED_APPS = [
    # ... your other apps
    'django_dispatch',
]

OUTBOX_PUBLISHERS = {
    'default': {
        'BACKEND': 'django_dispatch.backends.RedisStreamBackend',
        'OPTIONS': {
            'host': 'localhost',
            'port': 6379,
            'stream_name': 'events',
        }
    }
}
```

## Usage
```python
from django_dispatch.publishers import publisher

# Publish an event
event = publisher.publish_event(
    event_type='user.created',
    source='user-service',
    data={'user_id': 123, 'email': 'user@example.com'}
)

# Register event handler
from django_dispatch.registry import event_registry

@event_registry.register('user.created')
def handle_user_created(event):
    print(f"User created: {event.data}")
```
## Running the Worker

```bash
python manage.py outbox_worker
```
## Documentation
Full documentation is available at https://django-dispatch.readthedocs.io/en/latest/.

### Building and Serving Documentation Locally

To build the documentation locally:

```bash
# Build the documentation
make docs-build

# Serve the documentation locally at http://localhost:8080
make docs-serve
```

After running `make docs-serve`, you can access the documentation by opening http://localhost:8080 in your web browser.

## Contributing
Contributions are welcome! Please read our Contributing Guide for details.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
