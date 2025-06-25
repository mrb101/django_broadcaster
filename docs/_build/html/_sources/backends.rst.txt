Backends
========

Django Dispatch supports multiple backend implementations for publishing events to different systems. This page documents the available backends and how to configure them.

Redis Stream Backend
------------------

The Redis Stream backend publishes events to a Redis Stream, which is a powerful append-only data structure in Redis that allows for efficient message queuing and processing.

Configuration
^^^^^^^^^^^

.. code-block:: python

    OUTBOX_PUBLISHERS = {
        'default': {
            'BACKEND': 'django_dispatch.backends.RedisStreamBackend',
            'OPTIONS': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'password': None,
                'stream_name': 'events',
                'max_len': 10000,
                'connect_timeout': 5,
                'socket_timeout': 5,
            }
        }
    }

Options
^^^^^^

* ``host``: Redis server hostname (default: 'localhost')
* ``port``: Redis server port (default: 6379)
* ``db``: Redis database number (default: 0)
* ``password``: Redis password (optional)
* ``stream_name``: Name of the Redis stream (default: 'events')
* ``max_len``: Maximum length of the stream (default: 10000)
* ``connect_timeout``: Connection timeout in seconds (default: 5)
* ``socket_timeout``: Socket timeout in seconds (default: 5)

Consuming Events
^^^^^^^^^^^^^

To consume events from a Redis Stream, you can use the Redis client directly:

.. code-block:: python

    import redis
    import json

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Read from the stream
    messages = r.xread({'events': '0'}, count=10, block=1000)
    
    for stream_name, stream_messages in messages:
        for message_id, message_data in stream_messages:
            # Parse the CloudEvent
            cloud_event = json.loads(message_data[b'cloud_event'].decode('utf-8'))
            
            # Process the event
            print(f"Received event: {cloud_event['type']} - {cloud_event['id']}")
            
            # Acknowledge the message
            r.xack(stream_name, 'consumer_group', message_id)

Creating a Custom Backend
-----------------------

You can create custom backends by implementing the ``PublisherBackend`` abstract base class:

.. code-block:: python

    from django_dispatch.backends import PublisherBackend
    from django_dispatch.models import OutboxEvent

    class MyCustomBackend(PublisherBackend):
        """
        Custom publisher backend implementation
        """
        
        def __init__(self, config):
            self.config = config
            # Initialize your backend with the provided configuration
            
        def publish(self, event: OutboxEvent) -> bool:
            """
            Publish an event to your custom backend
            
            Args:
                event: The OutboxEvent to publish
                
            Returns:
                bool: True if successful, False otherwise
            """
            try:
                # Convert to CloudEvent format
                cloud_event = event.to_cloud_event()
                
                # Implement your publishing logic here
                # ...
                
                return True
            except Exception as e:
                # Log the error and re-raise
                raise
                
        def health_check(self) -> bool:
            """
            Check if the backend is healthy and available
            
            Returns:
                bool: True if healthy, False otherwise
            """
            try:
                # Implement your health check logic here
                # ...
                return True
            except Exception:
                return False

Registering a Custom Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^

To use your custom backend, you need to register it in the publisher:

.. code-block:: python

    # In your app's apps.py or a module that runs at startup

    from django_dispatch.publishers import publisher
    from myapp.backends import MyCustomBackend

    def register_custom_backend():
        publisher._backends['my_custom'] = MyCustomBackend({
            'option1': 'value1',
            'option2': 'value2',
        })

    # Call this function during app initialization
