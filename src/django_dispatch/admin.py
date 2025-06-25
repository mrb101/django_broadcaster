from django.contrib import admin
from django.utils.html import format_html

from .models import OutboxEvent, OutboxEventStatus


@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "event_type",
        "source",
        "status_display",
        "created_at",
        "retry_count",
        "scheduled_at",
    ]
    list_filter = [
        "status",
        "event_type",
        "source",
        "created_at",
        "publisher_backend",
        "retry_count",
    ]
    search_fields = ["id", "event_type", "source", "subject"]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "published_at",
        "retry_count",
        "last_error",
    ]
    fieldsets = [
        (
            "Event Information",
            {
                "fields": [
                    "id",
                    "event_type",
                    "source",
                    "subject",
                    "spec_version",
                    "data_content_type",
                    "data_schema",
                ]
            },
        ),
        ("Event Data", {"fields": ["data"], "classes": ["collapse"]}),
        (
            "Publishing",
            {
                "fields": [
                    "status",
                    "publisher_backend",
                    "publisher_config",
                    "scheduled_at",
                    "published_at",
                ]
            },
        ),
        (
            "Retry & Error Handling",
            {"fields": ["retry_count", "max_retries", "last_error"]},
        ),
        (
            "Timestamps",
            {"fields": ["created_at", "updated_at"], "classes": ["collapse"]},
        ),
    ]

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            OutboxEventStatus.PENDING: "orange",
            OutboxEventStatus.PROCESSING: "blue",
            OutboxEventStatus.PUBLISHED: "green",
            OutboxEventStatus.FAILED: "red",
            OutboxEventStatus.RETRY: "purple",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    actions = ["retry_failed_events", "mark_as_failed"]

    def retry_failed_events(self, request, queryset):
        """Action to retry failed events"""
        failed_events = queryset.filter(status=OutboxEventStatus.FAILED)
        count = failed_events.update(
            status=OutboxEventStatus.PENDING, retry_count=0, last_error=""
        )
        self.message_user(request, f"{count} events marked for retry.")

    retry_failed_events.short_description = "Retry selected failed events"

    def mark_as_failed(self, request, queryset):
        """Action to mark events as failed"""
        count = queryset.update(status=OutboxEventStatus.FAILED)
        self.message_user(request, f"{count} events marked as failed.")

    mark_as_failed.short_description = "Mark selected events as failed"
