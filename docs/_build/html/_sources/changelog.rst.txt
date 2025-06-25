Changelog
=========

All notable changes to Django Dispatch will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
-----------

Added
~~~~~

* Initial project structure
* OutboxEvent model for storing events
* CloudEvent implementation
* Event registry for handling events
* Redis Stream backend
* Django admin integration
* Management command for processing events
* Comprehensive documentation

[0.1.0] - 2023-10-01
-------------------

* Initial release
* Basic functionality for the outbox pattern
* Redis Stream backend
* Event handling registry
* CloudEvents compatibility
