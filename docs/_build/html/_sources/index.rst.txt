Django Dispatch
==============

.. image:: https://badge.fury.io/py/django-outbox.svg
   :target: https://badge.fury.io/py/django-outbox
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/django-outbox.svg
   :target: https://pypi.org/project/django-outbox/
   :alt: Python versions

.. image:: https://img.shields.io/pypi/djversions/django-outbox.svg
   :target: https://pypi.org/project/django-outbox/
   :alt: Django versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/yourusername/django-outbox/blob/main/LICENSE
   :alt: License

A Django app that implements the transactional outbox pattern with CloudEvents support, enabling reliable event publishing in distributed systems.

Features
--------

- 🔄 **Transactional Outbox Pattern**: Ensures events are published reliably
- ☁️ **CloudEvents Compatible**: Follows CloudEvents specification
- 🔌 **Multiple Backends**: Redis Streams, Coming soon (Kafka, NATS support)
- 🔁 **Retry Logic**: Exponential backoff with configurable retries
- 📊 **Monitoring**: Built-in metrics and health checks (Comming soon)
- 🎯 **Event Handlers**: Local event processing framework
- 🔧 **Admin Interface**: Django admin integration

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   configuration
   usage
   backends
   
.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/models
   api/events
   api/publishers
   api/registry
   api/backends
   api/signals
   
.. toctree::
   :maxdepth: 1
   :caption: Development
   
   contributing
   changelog

Indices and tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
