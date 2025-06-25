from unittest.mock import MagicMock, patch

import pytest
from django.db.models.signals import post_save

from django_dispatch.models import OutboxEvent, OutboxEventStatus
from django_dispatch.registry import event_created, event_published
from django_dispatch.signals import handle_outbox_event_signals


@pytest.mark.django_db
def test_handle_outbox_event_signals_created():
    """Test that the event_created signal is sent when an OutboxEvent is created"""
    # Mock the event_created signal
    with patch("django_dispatch.signals.event_created.send") as mock_event_created:
        # Mock the event_registry
        with patch(
            "django_dispatch.signals.event_registry.handle_event"
        ) as mock_handle_event:
            # Create a new OutboxEvent
            event = OutboxEvent.objects.create(
                event_type="test.event", source="test-source"
            )

            # Check that event_created.send was called with the correct arguments
            mock_event_created.assert_called_once()
            args, kwargs = mock_event_created.call_args
            assert kwargs["sender"] == OutboxEvent
            assert kwargs["event"] == event

            # Check that event_registry.handle_event was called with the event
            mock_handle_event.assert_called_once_with(event)


@pytest.mark.django_db
def test_handle_outbox_event_signals_published():
    """Test that the event_published signal is sent when an OutboxEvent is marked as published"""
    # Create a new OutboxEvent
    event = OutboxEvent.objects.create(event_type="test.event", source="test-source")

    # Mock the event_published signal
    with patch("django_dispatch.signals.event_published.send") as mock_event_published:
        # Update the event to PUBLISHED status
        event.status = OutboxEventStatus.PUBLISHED
        event.save()

        # Check that event_published.send was called with the correct arguments
        mock_event_published.assert_called_once()
        args, kwargs = mock_event_published.call_args
        assert kwargs["sender"] == OutboxEvent
        assert kwargs["event"] == event


@pytest.mark.django_db
def test_signal_connection():
    """Test that the handle_outbox_event_signals function is connected to the post_save signal"""
    # Create a mock receiver
    mock_receiver = MagicMock()

    # Temporarily disconnect our signal handler
    post_save.disconnect(handle_outbox_event_signals, sender=OutboxEvent)

    try:
        # Connect our mock receiver
        post_save.connect(mock_receiver, sender=OutboxEvent)

        # Create a new OutboxEvent
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Check that our mock receiver was called
        mock_receiver.assert_called_once()

        # Update the event
        event.status = OutboxEventStatus.PUBLISHED
        event.save()

        # Check that our mock receiver was called again
        assert mock_receiver.call_count == 2

    finally:
        # Disconnect our mock receiver
        post_save.disconnect(mock_receiver, sender=OutboxEvent)

        # Reconnect the original signal handler
        post_save.connect(handle_outbox_event_signals, sender=OutboxEvent)


@pytest.mark.django_db
def test_event_created_signal():
    """Test that we can connect to the event_created signal"""
    # Create a mock receiver
    mock_receiver = MagicMock()

    # Connect our mock receiver to the event_created signal
    event_created.connect(mock_receiver)

    try:
        # Create a new OutboxEvent
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Check that our mock receiver was called
        mock_receiver.assert_called_once()
        args, kwargs = mock_receiver.call_args
        assert kwargs["sender"] == OutboxEvent
        assert kwargs["event"] == event

    finally:
        # Disconnect our mock receiver
        event_created.disconnect(mock_receiver)


@pytest.mark.django_db
def test_event_published_signal():
    """Test that we can connect to the event_published signal"""
    # Create a mock receiver
    mock_receiver = MagicMock()

    # Connect our mock receiver to the event_published signal
    event_published.connect(mock_receiver)

    try:
        # Create a new OutboxEvent
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Update the event to PUBLISHED status
        event.status = OutboxEventStatus.PUBLISHED
        event.save()

        # Check that our mock receiver was called
        mock_receiver.assert_called_once()
        args, kwargs = mock_receiver.call_args
        assert kwargs["sender"] == OutboxEvent
        assert kwargs["event"] == event

    finally:
        # Disconnect our mock receiver
        event_published.disconnect(mock_receiver)
