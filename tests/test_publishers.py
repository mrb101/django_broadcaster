from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from django_broadcaster.events import CloudEvent
from django_broadcaster.models import OutboxEvent, OutboxEventStatus
from django_broadcaster.publishers import OutboxPublisher


class TestOutboxPublisher:
    """Tests for the OutboxPublisher class"""

    def test_initialization(self):
        """Test that OutboxPublisher initializes and loads backends"""
        with patch("django_broadcaster.publishers.getattr") as mock_getattr:
            # Mock settings.OUTBOX_PUBLISHERS
            mock_getattr.return_value = {
                "test_backend": {
                    "BACKEND": "django_broadcaster.backends.RedisStreamBackend",
                    "OPTIONS": {"host": "test-host"},
                }
            }

            with patch("django_broadcaster.publishers.RedisStreamBackend") as mock_backend:
                publisher = OutboxPublisher()

                # Check that the backend was loaded
                mock_backend.assert_called_once_with({"host": "test-host"})
                assert "test_backend" in publisher._backends

    @pytest.mark.django_db
    def test_publish_event(self):
        """Test that publish_event creates an OutboxEvent"""
        publisher = OutboxPublisher()

        # Call publish_event
        event = publisher.publish_event(
            event_type="test.event",
            source="test-source",
            data={"test": "data"},
            subject="test-subject",
            backend="test_backend",
            scheduled_at=timezone.now(),
            max_retries=5,
            publisher_config={"key": "value"},
        )

        # Check that the event was created with the correct attributes
        assert isinstance(event, OutboxEvent)
        assert event.event_type == "test.event"
        assert event.source == "test-source"
        assert event.data == {"test": "data"}
        assert event.subject == "test-subject"
        assert event.publisher_backend == "test_backend"
        assert event.max_retries == 5
        assert event.publisher_config == {"key": "value"}
        assert event.status == OutboxEventStatus.PENDING

    @pytest.mark.django_db
    def test_publish_cloud_event(self):
        """Test that publish_cloud_event creates an OutboxEvent from a CloudEvent"""
        publisher = OutboxPublisher()

        # Create a CloudEvent
        cloud_event = CloudEvent(
            event_type="test.event",
            source="test-source",
            data={"test": "data"},
            subject="test-subject",
        )

        # Call publish_cloud_event
        event = publisher.publish_cloud_event(
            cloud_event=cloud_event,
            backend="test_backend",
            scheduled_at=timezone.now(),
            max_retries=5,
            publisher_config={"key": "value"},
        )

        # Check that the event was created with the correct attributes
        assert isinstance(event, OutboxEvent)
        assert event.event_type == "test.event"
        assert event.source == "test-source"
        assert event.data == {"test": "data"}
        assert event.subject == "test-subject"
        assert event.publisher_backend == "test_backend"
        assert event.max_retries == 5
        assert event.publisher_config == {"key": "value"}
        assert event.status == OutboxEventStatus.PENDING

    @pytest.mark.django_db
    def test_process_pending_events(self):
        """Test that process_pending_events processes pending events"""
        publisher = OutboxPublisher()

        # Create some test events
        event1 = OutboxEvent.objects.create(
            event_type="test.event.1", source="test-source", scheduled_at=timezone.now()
        )

        event2 = OutboxEvent.objects.create(
            event_type="test.event.2", source="test-source", scheduled_at=timezone.now()
        )

        # Mock _process_single_event to return True for event1 and False for event2
        publisher._process_single_event = MagicMock(side_effect=[True, False])

        # Call process_pending_events
        processed_count = publisher.process_pending_events()

        # Check that _process_single_event was called for both events
        assert publisher._process_single_event.call_count == 2

        # Check that the processed count is correct (only event1 was processed successfully)
        assert processed_count == 1

    @pytest.mark.django_db
    def test_process_single_event_success(self):
        """Test that _process_single_event successfully processes an event"""
        publisher = OutboxPublisher()

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event",
            source="test-source",
            publisher_backend="test_backend",
        )

        # Mock the backend
        mock_backend = MagicMock()
        mock_backend.health_check.return_value = True
        mock_backend.publish.return_value = True
        publisher._backends = {"test_backend": mock_backend}

        # Call _process_single_event
        result = publisher._process_single_event(event)

        # Check that the event was processed successfully
        assert result is True

        # Check that the event status was updated
        event.refresh_from_db()
        assert event.status == OutboxEventStatus.PUBLISHED
        assert event.published_at is not None

        # Check that the backend methods were called
        mock_backend.health_check.assert_called_once()
        mock_backend.publish.assert_called_once_with(event)

    @pytest.mark.django_db
    def test_process_single_event_failure(self):
        """Test that _process_single_event handles failures"""
        publisher = OutboxPublisher()

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event",
            source="test-source",
            publisher_backend="test_backend",
        )

        # Mock the backend to fail
        mock_backend = MagicMock()
        mock_backend.health_check.return_value = True
        mock_backend.publish.side_effect = Exception("Test error")
        publisher._backends = {"test_backend": mock_backend}

        # Call _process_single_event
        result = publisher._process_single_event(event)

        # Check that the event was not processed successfully
        assert result is False

        # Check that the event status was updated
        event.refresh_from_db()
        assert event.status == OutboxEventStatus.RETRY
        assert event.retry_count == 1
        assert "Test error" in event.last_error

        # Check that the backend methods were called
        mock_backend.health_check.assert_called_once()
        mock_backend.publish.assert_called_once_with(event)

    def test_get_backend_health(self):
        """Test that get_backend_health returns the health status of all backends"""
        publisher = OutboxPublisher()

        # Mock the backends
        mock_backend1 = MagicMock()
        mock_backend1.health_check.return_value = True

        mock_backend2 = MagicMock()
        mock_backend2.health_check.return_value = False

        publisher._backends = {"backend1": mock_backend1, "backend2": mock_backend2}

        # Call get_backend_health
        health = publisher.get_backend_health()

        # Check the result
        assert health == {"backend1": True, "backend2": False}

        # Check that health_check was called for both backends
        mock_backend1.health_check.assert_called_once()
        mock_backend2.health_check.assert_called_once()
