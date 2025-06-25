Configuration
============

Django Dispatch provides several configuration options that can be set in your Django settings file.

Basic Configuration
-----------------

At a minimum, you need to configure at least one publisher backend:

.. code-block:: python

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

Multiple Backends
---------------

You can configure multiple backends for different types of events:

.. code-block:: python

    OUTBOX_PUBLISHERS = {
        'default': {
            'BACKEND': 'django_dispatch.backends.RedisStreamBackend',
            'OPTIONS': {
                'host': 'localhost',
                'port': 6379,
                'stream_name': 'events',
            }
        },
        'high_priority': {
            'BACKEND': 'django_dispatch.backends.RedisStreamBackend',
            'OPTIONS': {
                'host': 'redis.example.com',
                'port': 6379,
                'stream_name': 'high_priority_events',
                'max_len': 100000,
            }
        }
    }

When publishing events, you can specify which backend to use:

.. code-block:: python

    from django_dispatch.publishers import publisher

    publisher.publish_event(
        event_type='user.created',
        source='user-service',
        data={'user_id': 123},
        backend='high_priority'  # Specify the backend
    )

Backend Options
-------------

Redis Stream Backend
^^^^^^^^^^^^^^^^^^

The Redis Stream backend supports the following options:

.. code-block:: python

    'OPTIONS': {
        'host': 'localhost',           # Redis host
        'port': 6379,                  # Redis port
        'db': 0,                       # Redis database number
        'password': None,              # Redis password (optional)
        'stream_name': 'events',       # Name of the Redis stream
        'max_len': 10000,              # Maximum length of the stream
        'connect_timeout': 5,          # Connection timeout in seconds
        'socket_timeout': 5,           # Socket timeout in seconds
    }

Worker Configuration
------------------

The outbox worker processes events from the outbox and publishes them to the configured backends. You can configure the worker behavior:

.. code-block:: python

    # Worker settings
    OUTBOX_WORKER = {
        'BATCH_SIZE': 100,             # Number of events to process in one batch
        'SLEEP_TIME': 5,               # Sleep time between batches in seconds
        'MAX_RETRIES': 3,              # Default maximum retry attempts
        'RETRY_BACKOFF': True,         # Use exponential backoff for retries
    }

Advanced Configuration
-------------------

Event Retention
^^^^^^^^^^^^^

You can configure how long to keep events in the database:

.. code-block:: python

    # Event retention settings
    OUTBOX_RETENTION = {
        'CLEANUP_PUBLISHED': True,     # Clean up published events
        'PUBLISHED_RETENTION_DAYS': 7, # Keep published events for 7 days
        'FAILED_RETENTION_DAYS': 30,   # Keep failed events for 30 days
    }

Logging
^^^^^^

Django Dispatch uses Python's logging module. You can configure logging in your Django settings:

.. code-block:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django_dispatch': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }
