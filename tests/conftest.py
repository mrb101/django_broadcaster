import os

import pytest
from django.conf import settings


def pytest_configure():
    """
    Configure Django settings for tests
    """
    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "django.contrib.admin",
            "django_broadcaster",
        ],
        SITE_ID=1,
        MIDDLEWARE=[],
        ROOT_URLCONF="tests.urls",
        SECRET_KEY="test-key",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
        OUTBOX_PUBLISHERS={
            "default": {
                "BACKEND": "django_broadcaster.backends.RedisStreamBackend",
                "OPTIONS": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "stream_name": "test_events",
                },
            }
        },
    )

    import django

    django.setup()


@pytest.fixture
def outbox_event():
    """
    Create a test OutboxEvent instance
    """
    from django_broadcaster.models import OutboxEvent

    event = OutboxEvent.objects.create(
        event_type="test.event",
        source="test-source",
        subject="test-subject",
        data={"test": "data"},
    )

    return event


@pytest.fixture
def cloud_event():
    """
    Create a test CloudEvent instance
    """
    from django_broadcaster.events import CloudEvent

    event = CloudEvent(
        event_type="test.event",
        source="test-source",
        subject="test-subject",
        data={"test": "data"},
    )

    return event


@pytest.fixture
def mock_redis(monkeypatch):
    """
    Mock Redis client for testing
    """

    class MockRedis:
        def __init__(self, *args, **kwargs):
            self.data = {}
            self.streams = {}

        def ping(self):
            return True

        def xadd(self, stream_name, data, maxlen=None, approximate=True):
            if stream_name not in self.streams:
                self.streams[stream_name] = []

            message_id = f"0-{len(self.streams[stream_name])}"
            self.streams[stream_name].append((message_id, data))
            return message_id

    monkeypatch.setattr("redis.Redis", MockRedis)
    return MockRedis()
