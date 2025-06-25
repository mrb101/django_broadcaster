Publishers API
============

.. module:: django_dispatch.publishers

This module contains the publisher classes used to publish events to the outbox.

OutboxPublisher
-------------

.. autoclass:: OutboxPublisher
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: _load_backends
   .. automethod:: publish_event
   .. automethod:: publish_cloud_event
   .. automethod:: process_pending_events
   .. automethod:: _process_single_event
   .. automethod:: _get_default_backend
   .. automethod:: get_backend_health

Singleton Instance
----------------

.. data:: publisher

   A singleton instance of :class:`OutboxPublisher` that is created when the module is imported.
   This is the recommended way to access the publisher functionality.

   Example usage:

   .. code-block:: python

       from django_dispatch.publishers import publisher

       event = publisher.publish_event(
           event_type='user.created',
           source='user-service',
           data={'user_id': 123}
       )
