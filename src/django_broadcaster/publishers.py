import logging
from datetime import datetime
from typing import Any, Dict, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .backends import PublisherBackend, RedisStreamBackend
from .events import CloudEvent
from .models import OutboxEvent, OutboxEventStatus

logger = logging.getLogger(__name__)


class OutboxPublisher:
    """
    Main publisher class for the outbox pattern
    """

    def __init__(self):
        self._backends: Dict[str, PublisherBackend] = {}
        self._load_backends()

    def _load_backends(self):
        """Load configured publisher backends"""
        outbox_config = getattr(settings, "OUTBOX_PUBLISHERS", {})

        for name, config in outbox_config.items():
            backend_class = config.get("BACKEND")
            backend_options = config.get("OPTIONS", {})

            if backend_class == "django_broadcaster.backends.RedisStreamBackend":
                self._backends[name] = RedisStreamBackend(backend_options)
            else:
                logger.warning(f"Unknown backend class: {backend_class}")

    def publish_event(
        self,
        event_type: str,
        source: str,
        data: Optional[Any] = None,
        subject: str = "",
        backend: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        publisher_config: Optional[Dict[str, Any]] = None,
    ) -> OutboxEvent:
        """
        Publish an event to the outbox

        Args:
            event_type: Type of the event
            source: Source of the event
            data: Event payload data
            subject: Event subject (optional)
            backend: Publisher backend to use (optional)
            scheduled_at: When to publish the event (default: now)
            max_retries: Maximum retry attempts
            publisher_config: Backend-specific configuration

        Returns:
            OutboxEvent: The created event
        """

        with transaction.atomic():
            event = OutboxEvent.objects.create(
                event_type=event_type,
                source=source,
                subject=subject,
                data=data,
                scheduled_at=scheduled_at or timezone.now(),
                max_retries=max_retries,
                publisher_backend=backend or "",
                publisher_config=publisher_config or {},
            )

            logger.info(f"Created outbox event: {event.id}")
            return event

    def publish_cloud_event(
        self,
        cloud_event: CloudEvent,
        backend: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        publisher_config: Optional[Dict[str, Any]] = None,
    ) -> OutboxEvent:
        """
        Publish a CloudEvent to the outbox
        """
        return self.publish_event(
            event_type=cloud_event.event_type,
            source=cloud_event.source,
            data=cloud_event.data,
            subject=cloud_event.subject,
            backend=backend,
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            publisher_config=publisher_config,
        )

    def process_pending_events(self, batch_size: int = 100) -> int:
        """
        Process pending events from the outbox

        Args:
            batch_size: Number of events to process in one batch

        Returns:
            int: Number of events processed
        """
        processed_count = 0

        # Get pending events that are ready to be published
        pending_events = OutboxEvent.objects.filter(
            status__in=[OutboxEventStatus.PENDING, OutboxEventStatus.RETRY],
            scheduled_at__lte=timezone.now(),
        ).order_by("created_at")[:batch_size]

        for event in pending_events:
            if self._process_single_event(event):
                processed_count += 1

        return processed_count

    def _process_single_event(self, event: OutboxEvent) -> bool:
        """
        Process a single event

        Args:
            event: The event to process

        Returns:
            bool: True if successfully processed, False otherwise
        """
        try:
            # Mark as processing to prevent concurrent processing
            with transaction.atomic():
                event_to_update = OutboxEvent.objects.select_for_update().get(
                    id=event.id
                )
                if event_to_update.status == OutboxEventStatus.PROCESSING:
                    return False  # Already being processed

                event_to_update.status = OutboxEventStatus.PROCESSING
                event_to_update.save(update_fields=["status", "updated_at"])
                event = event_to_update

            # Determine which backend to use
            backend_name = event.publisher_backend or self._get_default_backend()
            if not backend_name or backend_name not in self._backends:
                raise ValueError(f"No valid backend found: {backend_name}")

            backend = self._backends[backend_name]

            # Check backend health
            if not backend.health_check():
                raise Exception(f"Backend {backend_name} is not healthy")

            # Publish the event
            success = backend.publish(event)

            if success:
                event.mark_as_published()
                logger.info(f"Successfully published event {event.id}")
                return True
            else:
                raise Exception("Backend publish returned False")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to process event {event.id}: {error_msg}")
            event.increment_retry(error_msg)
            return False

    def _get_default_backend(self) -> Optional[str]:
        """Get the default backend name"""
        if self._backends:
            return next(iter(self._backends.keys()))
        return None

    def get_backend_health(self) -> Dict[str, bool]:
        """Get health status of all backends"""
        return {
            name: backend.health_check() for name, backend in self._backends.items()
        }


publisher = OutboxPublisher()
