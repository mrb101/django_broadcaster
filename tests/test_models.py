import pytest
from django.utils import timezone

from django_broadcaster.models import OutboxEvent, OutboxEventStatus


@pytest.mark.django_db
def test_outbox_event_creation():
    """Test that an OutboxEvent can be created with the correct attributes"""
    event = OutboxEvent.objects.create(
        event_type="test.event",
        source="test-source",
        subject="test-subject",
        data={"test": "data"},
    )

    assert str(event) == f"test.event - {event.id}"
    assert event.status == OutboxEventStatus.PENDING
    assert event.retry_count == 0
    assert event.max_retries == 3
    assert event.last_error == ""
    assert event.publisher_backend == ""
    assert event.publisher_config == {}


@pytest.mark.django_db
def test_outbox_event_to_cloud_event():
    """Test that an OutboxEvent can be converted to a CloudEvent format"""
    event = OutboxEvent.objects.create(
        event_type="test.event",
        source="test-source",
        subject="test-subject",
        data={"test": "data"},
        data_content_type="application/json",
        data_schema="https://example.com/schema",
    )

    cloud_event = event.to_cloud_event()

    assert cloud_event["specversion"] == "1.0"
    assert cloud_event["type"] == "test.event"
    assert cloud_event["source"] == "test-source"
    assert cloud_event["subject"] == "test-subject"
    assert cloud_event["datacontenttype"] == "application/json"
    assert cloud_event["dataschema"] == "https://example.com/schema"
    assert cloud_event["data"] == {"test": "data"}
    assert cloud_event["id"] == str(event.id)
    assert "time" in cloud_event


@pytest.mark.django_db
def test_outbox_event_mark_as_published():
    """Test that an OutboxEvent can be marked as published"""
    event = OutboxEvent.objects.create(event_type="test.event", source="test-source")

    assert event.status == OutboxEventStatus.PENDING
    assert event.published_at is None

    event.mark_as_published()

    # Refresh from database
    event.refresh_from_db()

    assert event.status == OutboxEventStatus.PUBLISHED
    assert event.published_at is not None


@pytest.mark.django_db
def test_outbox_event_mark_as_failed():
    """Test that an OutboxEvent can be marked as failed"""
    event = OutboxEvent.objects.create(event_type="test.event", source="test-source")

    assert event.status == OutboxEventStatus.PENDING
    assert event.last_error == ""

    error_message = "Test error message"
    event.mark_as_failed(error_message)

    # Refresh from database
    event.refresh_from_db()

    assert event.status == OutboxEventStatus.FAILED
    assert event.last_error == error_message


@pytest.mark.django_db
def test_outbox_event_increment_retry():
    """Test that an OutboxEvent's retry count can be incremented"""
    event = OutboxEvent.objects.create(
        event_type="test.event", source="test-source", max_retries=3
    )

    assert event.retry_count == 0
    assert event.status == OutboxEventStatus.PENDING

    # First retry
    event.increment_retry("First retry")
    event.refresh_from_db()

    assert event.retry_count == 1
    assert event.status == OutboxEventStatus.RETRY
    assert event.last_error == "First retry"

    # Second retry
    event.increment_retry("Second retry")
    event.refresh_from_db()

    assert event.retry_count == 2
    assert event.status == OutboxEventStatus.RETRY
    assert event.last_error == "Second retry"

    # Third retry - should mark as failed
    event.increment_retry("Third retry")
    event.refresh_from_db()

    assert event.retry_count == 3
    assert event.status == OutboxEventStatus.FAILED
    assert event.last_error == "Third retry"


@pytest.mark.django_db
def test_outbox_event_fixture(outbox_event):
    """Test that the outbox_event fixture works correctly"""
    assert outbox_event.event_type == "test.event"
    assert outbox_event.source == "test-source"
    assert outbox_event.subject == "test-subject"
    assert outbox_event.data == {"test": "data"}
    assert outbox_event.status == OutboxEventStatus.PENDING
