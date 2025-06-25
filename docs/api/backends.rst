Backends API
===========

.. module:: django_dispatch.backends

This module contains the backend classes used to publish events to external systems.

PublisherBackend
--------------

.. autoclass:: PublisherBackend
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: publish
   .. automethod:: health_check
   .. automethod:: get_name

RedisStreamBackend
----------------

.. autoclass:: RedisStreamBackend
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: publish
   .. automethod:: health_check
   .. automethod:: get_name

Creating Custom Backends
----------------------

To create a custom backend, you need to subclass :class:`PublisherBackend` and implement the required methods:

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
            """
            try:
                # Implement your health check logic here
                # ...
                return True
            except Exception:
                return False
