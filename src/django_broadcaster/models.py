import uuid
from typing import Any, Dict

from django.db import models
from django.utils import timezone


class OutboxEventStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    PUBLISHED = "published", "Published"
    FAILED = "failed", "Failed"
    RETRY = "retry", "Retry"


class OutboxEvent(models.Model):
    """
    Stores events to be published following the outbox pattern.
    Compatible with CloudEvents specification.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # CloudEvents required attributes
    spec_version = models.CharField(max_length=10, default="1.0")
    event_type = models.CharField(max_length=255, db_index=True)
    source = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)

    # CloudEvents optional attributes
    data_content_type = models.CharField(max_length=100, default="application/json")
    data_schema = models.URLField(blank=True)

    # Event data (serialized JSON)
    data = models.JSONField(null=True, blank=True)

    # Outbox specific fields
    status = models.CharField(
        max_length=20,
        choices=OutboxEventStatus.choices,
        default=OutboxEventStatus.PENDING,
        db_index=True,
    )

    # Timing fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_at = models.DateTimeField(default=timezone.now, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Retry and error handling
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    last_error = models.TextField(blank=True)

    # Publisher configuration
    publisher_backend = models.CharField(max_length=100, blank=True)
    publisher_config = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "outbox_events"
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.id}"

    def to_cloud_event(self) -> Dict[str, Any]:
        """Convert to CloudEvents format"""
        event = {
            "specversion": self.spec_version,
            "type": self.event_type,
            "source": self.source,
            "id": str(self.id),
            "time": self.created_at.isoformat(),
        }

        if self.subject:
            event["subject"] = self.subject
        if self.data_content_type:
            event["datacontenttype"] = self.data_content_type
        if self.data_schema:
            event["dataschema"] = self.data_schema
        if self.data is not None:
            event["data"] = self.data

        return event

    def mark_as_published(self):
        """Mark event as successfully published"""
        self.status = OutboxEventStatus.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at", "updated_at"])

    def mark_as_failed(self, error_message: str):
        """Mark event as failed with error details"""
        self.status = OutboxEventStatus.FAILED
        self.last_error = error_message
        self.save(update_fields=["status", "last_error", "updated_at"])

    def increment_retry(self, error_message: str = ""):
        """Increment retry count and handle retry logic"""
        self.retry_count += 1
        if error_message:
            self.last_error = error_message

        if self.retry_count >= self.max_retries:
            self.status = OutboxEventStatus.FAILED
        else:
            self.status = OutboxEventStatus.RETRY
            # Exponential backoff: 2^retry_count minutes
            delay_minutes = 2**self.retry_count
            self.scheduled_at = timezone.now() + timezone.timedelta(
                minutes=delay_minutes
            )

        self.save(
            update_fields=[
                "retry_count",
                "last_error",
                "status",
                "scheduled_at",
                "updated_at",
            ]
        )
