from unittest.mock import MagicMock

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from django_dispatch.admin import OutboxEventAdmin
from django_dispatch.models import OutboxEvent, OutboxEventStatus


class TestOutboxEventAdmin:
    """Tests for the OutboxEventAdmin class"""

    @pytest.fixture
    def admin_site(self):
        return AdminSite()

    @pytest.fixture
    def admin_instance(self, admin_site):
        return OutboxEventAdmin(OutboxEvent, admin_site)

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def mock_request(self, request_factory):
        request = request_factory.get("/")
        request.session = "session"
        request._messages = FallbackStorage(request)
        return request

    def test_status_display(self, admin_instance):
        """Test that status_display returns HTML with the correct color"""
        # Create events with different statuses
        pending_event = MagicMock(status=OutboxEventStatus.PENDING)
        pending_event.get_status_display.return_value = "Pending"

        processing_event = MagicMock(status=OutboxEventStatus.PROCESSING)
        processing_event.get_status_display.return_value = "Processing"

        published_event = MagicMock(status=OutboxEventStatus.PUBLISHED)
        published_event.get_status_display.return_value = "Published"

        failed_event = MagicMock(status=OutboxEventStatus.FAILED)
        failed_event.get_status_display.return_value = "Failed"

        retry_event = MagicMock(status=OutboxEventStatus.RETRY)
        retry_event.get_status_display.return_value = "Retry"

        # Check that each status has the correct color
        assert "color: orange" in admin_instance.status_display(pending_event)
        assert "Pending" in admin_instance.status_display(pending_event)

        assert "color: blue" in admin_instance.status_display(processing_event)
        assert "Processing" in admin_instance.status_display(processing_event)

        assert "color: green" in admin_instance.status_display(published_event)
        assert "Published" in admin_instance.status_display(published_event)

        assert "color: red" in admin_instance.status_display(failed_event)
        assert "Failed" in admin_instance.status_display(failed_event)

        assert "color: purple" in admin_instance.status_display(retry_event)
        assert "Retry" in admin_instance.status_display(retry_event)

    @pytest.mark.django_db
    def test_retry_failed_events(self, admin_instance, mock_request):
        """Test that retry_failed_events updates failed events"""
        # Create some test events
        failed_event1 = OutboxEvent.objects.create(
            event_type="test.event.1",
            source="test-source",
            status=OutboxEventStatus.FAILED,
            retry_count=2,
            last_error="Test error",
        )

        failed_event2 = OutboxEvent.objects.create(
            event_type="test.event.2",
            source="test-source",
            status=OutboxEventStatus.FAILED,
            retry_count=3,
            last_error="Another error",
        )

        # Create a non-failed event
        pending_event = OutboxEvent.objects.create(
            event_type="test.event.3",
            source="test-source",
            status=OutboxEventStatus.PENDING,
        )

        # Get all events
        queryset = OutboxEvent.objects.all()

        # Call the action
        admin_instance.retry_failed_events(mock_request, queryset)

        # Refresh the events from the database
        failed_event1.refresh_from_db()
        failed_event2.refresh_from_db()
        pending_event.refresh_from_db()

        # Check that failed events were updated
        assert failed_event1.status == OutboxEventStatus.PENDING
        assert failed_event1.retry_count == 0
        assert failed_event1.last_error == ""

        assert failed_event2.status == OutboxEventStatus.PENDING
        assert failed_event2.retry_count == 0
        assert failed_event2.last_error == ""

        # Check that the pending event was not affected
        assert pending_event.status == OutboxEventStatus.PENDING

    @pytest.mark.django_db
    def test_mark_as_failed(self, admin_instance, mock_request):
        """Test that mark_as_failed updates events to failed status"""
        # Create some test events
        event1 = OutboxEvent.objects.create(
            event_type="test.event.1",
            source="test-source",
            status=OutboxEventStatus.PENDING,
        )

        event2 = OutboxEvent.objects.create(
            event_type="test.event.2",
            source="test-source",
            status=OutboxEventStatus.PROCESSING,
        )

        # Get all events
        queryset = OutboxEvent.objects.all()

        # Call the action
        admin_instance.mark_as_failed(mock_request, queryset)

        # Refresh the events from the database
        event1.refresh_from_db()
        event2.refresh_from_db()

        # Check that all events were marked as failed
        assert event1.status == OutboxEventStatus.FAILED
        assert event2.status == OutboxEventStatus.FAILED
