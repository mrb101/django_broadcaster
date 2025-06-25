Installation
===========

Requirements
-----------

Django Dispatch requires:

* Python 3.8 or newer
* Django 3.2 or newer
* Redis (for the Redis Stream backend)

Installing Django Dispatch
-------------------------

You can install Django Dispatch using pip:

.. code-block:: bash

    pip install django-dispatch

Or if you're using uv:

.. code-block:: bash

    uv add django-dispatch

Adding to Your Django Project
----------------------------

1. Add ``django_dispatch`` to your ``INSTALLED_APPS`` in your Django settings:

   .. code-block:: python

       INSTALLED_APPS = [
           # ... other apps
           'django_dispatch',
       ]

2. Run migrations to create the necessary database tables:

   .. code-block:: bash

       python manage.py migrate django_dispatch

3. Configure the publisher backends in your Django settings (see :doc:`configuration` for details):

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

Next Steps
---------

Once you have installed Django Dispatch, you can:

* Learn about :doc:`configuration` options
* See :doc:`usage` examples
* Explore available :doc:`backends`
