Models API
=========

.. module:: django_broadcaster.models

This module contains the database models used by Django Dispatch.

OutboxEvent
----------

.. autoclass:: OutboxEvent
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: __str__
   .. automethod:: to_cloud_event
   .. automethod:: mark_as_published
   .. automethod:: mark_as_failed
   .. automethod:: increment_retry

OutboxEventStatus
---------------

.. autoclass:: OutboxEventStatus
   :members:
   :undoc-members:
   :show-inheritance:
