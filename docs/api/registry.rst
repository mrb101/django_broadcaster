Registry API
===========

.. module:: django_broadcaster.registry

This module contains the event handler registry and signals used by Django Dispatch.

EventHandlerRegistry
------------------

.. autoclass:: EventHandlerRegistry
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: register
   .. automethod:: handle_event
   .. automethod:: get_handlers
   .. automethod:: clear_handlers

Singleton Instance
----------------

.. data:: event_registry

   A singleton instance of :class:`EventHandlerRegistry` that is created when the module is imported.
   This is the recommended way to access the registry functionality.

   Example usage:

   .. code-block:: python

       from django_broadcaster.registry import event_registry

       @event_registry.register('user.created')
       def handle_user_created(event):
           print(f"User created: {event.data}")

Signals
------

.. data:: event_created

   A Django signal that is dispatched when an event is created.

   Signal arguments:
   
   * ``sender``: The sender of the signal (OutboxEvent class)
   * ``event``: The OutboxEvent instance that was created

   Example usage:

   .. code-block:: python

       from django.dispatch import receiver
       from django_broadcaster.registry import event_created

       @receiver(event_created)
       def handle_event_created(sender, event, **kwargs):
           print(f"Event created: {event.event_type}")

.. data:: event_published

   A Django signal that is dispatched when an event is published.

   Signal arguments:
   
   * ``sender``: The sender of the signal (OutboxEvent class)
   * ``event``: The OutboxEvent instance that was published

   Example usage:

   .. code-block:: python

       from django.dispatch import receiver
       from django_broadcaster.registry import event_published

       @receiver(event_published)
       def handle_event_published(sender, event, **kwargs):
           print(f"Event published: {event.event_type}")
