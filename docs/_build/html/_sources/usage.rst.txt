Usage
=====

This guide covers the basic usage of Django Dispatch for publishing and handling events.

Publishing Events
---------------

Django Dispatch provides several ways to publish events.

Basic Event Publishing
^^^^^^^^^^^^^^^^^^^

The simplest way to publish an event is using the publisher:

.. code-block:: python

    from django_dispatch.publishers import publisher

    # Publish an event
    event = publisher.publish_event(
        event_type='user.created',
        source='user-service',
        data={'user_id': 123, 'email': 'user@example.com'}
    )

This creates an event in the outbox that will be published by the worker process.

Publishing CloudEvents
^^^^^^^^^^^^^^^^^^^

You can also create and publish CloudEvents directly:

.. code-block:: python

    from django_dispatch.events import CloudEvent
    from django_dispatch.publishers import publisher

    # Create a CloudEvent
    cloud_event = CloudEvent(
        event_type='order.completed',
        source='order-service',
        data={'order_id': 456, 'total': 99.99},
        subject='Order #456'
    )

    # Publish the CloudEvent
    event = publisher.publish_cloud_event(cloud_event)

Scheduling Events
^^^^^^^^^^^^^^^

You can schedule events to be published at a specific time:

.. code-block:: python

    from datetime import timedelta
    from django.utils import timezone

    # Schedule an event for 1 hour from now
    scheduled_time = timezone.now() + timedelta(hours=1)
    
    event = publisher.publish_event(
        event_type='reminder.send',
        source='reminder-service',
        data={'user_id': 123, 'message': 'Remember to complete your profile'},
        scheduled_at=scheduled_time
    )

Handling Events
-------------

Django Dispatch provides a registry for handling events locally.

Registering Event Handlers
^^^^^^^^^^^^^^^^^^^^^^^^

You can register handlers for specific event types:

.. code-block:: python

    from django_dispatch.registry import event_registry

    @event_registry.register('user.created')
    def handle_user_created(event):
        """Handle user created events"""
        print(f"User created: {event.data}")
        # Do something with the event

    # Register a handler for multiple event types
    @event_registry.register('order.created')
    @event_registry.register('order.updated')
    def handle_order_events(event):
        """Handle order events"""
        print(f"Order event: {event.event_type} - {event.data}")
        # Do something with the event

Global Event Handlers
^^^^^^^^^^^^^^^^^^^

You can also register global handlers that receive all events:

.. code-block:: python

    @event_registry.register()  # No event_type means handle all events
    def log_all_events(event):
        """Log all events"""
        print(f"Event received: {event.event_type} from {event.source}")

Running the Worker
----------------

To process events from the outbox and publish them to the configured backends, you need to run the outbox worker:

.. code-block:: bash

    python manage.py outbox_worker

For production use, you should run the worker as a background service using a process manager like Supervisor, systemd, or Kubernetes.

Example Configuration for Supervisor:

.. code-block:: ini

    [program:outbox_worker]
    command=/path/to/venv/bin/python /path/to/project/manage.py outbox_worker
    directory=/path/to/project
    user=www-data
    autostart=true
    autorestart=true
    redirect_stderr=true
    stdout_logfile=/var/log/outbox_worker.log

Advanced Usage
------------

Transactional Publishing
^^^^^^^^^^^^^^^^^^^^^^

To ensure events are only published if a transaction is successful, use Django's transaction management:

.. code-block:: python

    from django.db import transaction
    from django_dispatch.publishers import publisher

    @transaction.atomic
    def create_user_with_event(username, email):
        # Create user in database
        user = User.objects.create(username=username, email=email)
        
        # Publish event - this will only be committed if the transaction succeeds
        publisher.publish_event(
            event_type='user.created',
            source='user-service',
            data={'user_id': user.id, 'email': user.email}
        )
        
        return user

Error Handling and Retries
^^^^^^^^^^^^^^^^^^^^^^^^

Django Dispatch automatically handles retries for failed events with exponential backoff:

.. code-block:: python

    # Configure max retries when publishing
    event = publisher.publish_event(
        event_type='notification.send',
        source='notification-service',
        data={'user_id': 123, 'message': 'Hello'},
        max_retries=5  # Override default max retries
    )

    # Check event status
    if event.status == 'failed':
        print(f"Event failed: {event.last_error}")
