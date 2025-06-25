from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OutboxEvent, OutboxEventStatus
from .registry import event_created, event_published, event_registry


@receiver(post_save, sender=OutboxEvent)
def handle_outbox_event_signals(sender, instance, created, **kwargs):
    """Handle signals for outbox events"""
    if created:
        # Dispatch event created signal
        event_created.send(sender=sender, event=instance)

        # Handle event locally if handlers are registered
        event_registry.handle_event(instance)

    elif instance.status == OutboxEventStatus.PUBLISHED:
        # Dispatch event published signal
        event_published.send(sender=sender, event=instance)
