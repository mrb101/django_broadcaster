import json
from unittest.mock import MagicMock, patch

import pytest

from django_broadcaster.backends import PublisherBackend, RedisStreamBackend
from django_broadcaster.models import OutboxEvent


class TestPublisherBackend:
    """Tests for the PublisherBackend abstract class"""

    def test_get_name(self):
        """Test that get_name returns the class name"""

        # Create a concrete subclass for testing
        class TestBackend(PublisherBackend):
            def publish(self, event):
                return True

            def health_check(self):
                return True

        backend = TestBackend()
        assert backend.get_name() == "TestBackend"


class TestRedisStreamBackend:
    """Tests for the RedisStreamBackend class"""

    def test_initialization(self):
        """Test that RedisStreamBackend initializes with the correct configuration"""
        config = {
            "host": "test-host",
            "port": 1234,
            "db": 5,
            "password": "test-password",
            "stream_name": "test-stream",
            "max_len": 5000,
        }

        with patch("redis.Redis") as mock_redis:
            backend = RedisStreamBackend(config)

            # Check that Redis client was initialized with correct params
            mock_redis.assert_called_once_with(
                host="test-host",
                port=1234,
                db=5,
                password="test-password",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )

            assert backend.stream_name == "test-stream"
            assert backend.max_len == 5000

    def test_initialization_defaults(self):
        """Test that RedisStreamBackend uses default values when not provided"""
        config = {}

        with patch("redis.Redis") as mock_redis:
            backend = RedisStreamBackend(config)

            # Check that Redis client was initialized with default params
            mock_redis.assert_called_once_with(
                host="localhost",
                port=6379,
                db=0,
                password=None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )

            assert backend.stream_name == "events"
            assert backend.max_len == 10000

    @pytest.mark.django_db
    def test_publish(self, mock_redis):
        """Test that publish adds the event to the Redis stream"""
        config = {"stream_name": "test-stream"}
        backend = RedisStreamBackend(config)

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event",
            source="test-source",
            subject="test-subject",
            data={"test": "data"},
        )

        # Mock the Redis client's xadd method
        backend.redis_client.xadd = MagicMock(return_value="0-1")

        # Call publish
        result = backend.publish(event)

        # Check that xadd was called with the correct parameters
        backend.redis_client.xadd.assert_called_once()
        args, kwargs = backend.redis_client.xadd.call_args

        assert args[0] == "test-stream"  # stream name
        assert "event_id" in args[1]
        assert args[1]["event_id"] == str(event.id)
        assert args[1]["event_type"] == "test.event"
        assert args[1]["source"] == "test-source"
        assert "cloud_event" in args[1]

        # Check that the cloud_event JSON is valid
        cloud_event = json.loads(args[1]["cloud_event"])
        assert cloud_event["type"] == "test.event"
        assert cloud_event["source"] == "test-source"
        assert cloud_event["subject"] == "test-subject"
        assert cloud_event["data"] == {"test": "data"}

        assert kwargs["maxlen"] == 10000
        assert kwargs["approximate"] is True

        # Check the result
        assert result is True

    def test_health_check_success(self):
        """Test that health_check returns True when Redis is healthy"""
        config = {}
        backend = RedisStreamBackend(config)

        # Mock the Redis client's ping method
        backend.redis_client.ping = MagicMock(return_value=True)

        # Call health_check
        result = backend.health_check()

        # Check that ping was called
        backend.redis_client.ping.assert_called_once()

        # Check the result
        assert result is True

    def test_health_check_failure(self):
        """Test that health_check returns False when Redis is not healthy"""
        config = {}
        backend = RedisStreamBackend(config)

        # Mock the Redis client's ping method to raise an exception
        backend.redis_client.ping = MagicMock(side_effect=Exception("Connection error"))

        # Call health_check
        result = backend.health_check()

        # Check that ping was called
        backend.redis_client.ping.assert_called_once()

        # Check the result
        assert result is False

    def test_get_name(self):
        """Test that get_name returns 'RedisStream'"""
        config = {}
        backend = RedisStreamBackend(config)

        assert backend.get_name() == "RedisStream"
