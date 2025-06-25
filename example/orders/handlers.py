import logging

from django_dispatch.models import OutboxEvent
from django_dispatch.registry import event_registry

logger = logging.getLogger(__name__)


@event_registry.register(event_type="order.created")
def handle_order_created(event: OutboxEvent):
    """
    Handler for order.created events

    This handler is called when a new order is created.
    It logs the event and could perform additional actions like:
    - Sending notifications
    - Updating analytics
    - Triggering integrations with other systems
    """
    order_id = event.data.get("order_id")
    customer_email = event.data.get("customer_email")
    total_amount = event.data.get("total_amount")

    logger.info(
        f"Order created handler: Order #{order_id} created by {customer_email} for ${total_amount}"
    )

    # Additional business logic can be implemented here
    # For example:
    # - Update inventory
    # - Send welcome email to new customers
    # - Notify fulfillment team


@event_registry.register(event_type="order.approved")
def handle_order_approved(event: OutboxEvent):
    """
    Handler for order.approved events

    This handler is called when an order is approved.
    It logs the event and could perform additional actions like:
    - Triggering fulfillment processes
    - Updating accounting systems
    - Sending notifications to warehouse
    """
    order_id = event.data.get("order_id")
    customer_email = event.data.get("customer_email")
    approved_at = event.data.get("approved_at")

    logger.info(
        f"Order approved handler: Order #{order_id} for {customer_email} was approved at {approved_at}"
    )

    # Additional business logic can be implemented here
    # For example:
    # - Trigger shipping process
    # - Update inventory
    # - Generate invoice
