Signals API
==========

.. module:: django_dispatch.signals

This module contains the signal handlers used by Django Dispatch.

Signal Handlers
-------------

.. autofunction:: handle_outbox_event_signals

Django Signals
------------

Django Dispatch uses the following signals from the :mod:`django_dispatch.registry` module:

* ``event_created``: Dispatched when an event is created
* ``event_published``: Dispatched when an event is published

See :doc:`registry` for more information on these signals.

Example Usage
-----------

.. code-block:: python

    from django.dispatch import receiver
    from django_dispatch.registry import event_created, event_published

    @receiver(event_created)
    def handle_event_created(sender, event, **kwargs):
        """Handle event created signal"""
        print(f"Event created: {event.event_type}")

    @receiver(event_published)
    def handle_event_published(sender, event, **kwargs):
        """Handle event published signal"""
        print(f"Event published: {event.event_type}")

Internal Signal Flow
-----------------

1. When an OutboxEvent is created, the post_save signal is triggered
2. The handle_outbox_event_signals function receives this signal
3. If the event is new (created=True), it dispatches the event_created signal
4. If the event's status is PUBLISHED, it dispatches the event_published signal

This signal flow allows for decoupled components to react to events being created or published.
