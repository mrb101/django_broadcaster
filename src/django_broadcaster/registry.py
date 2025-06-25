import logging
from typing import Any, Callable, Dict, List, Optional

from django.dispatch import Signal

from .models import OutboxEvent

logger = logging.getLogger(__name__)

# Signal dispatched when an event is created
event_created = Signal()

# Signal dispatched when an event is published
event_published = Signal()


class EventHandlerRegistry:
    """
    Registry for event handlers that can process events locally
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._global_handlers: List[Callable] = []

    def register(self, event_type: Optional[str] = None):
        """
        Decorator to register an event handler

        Args:
            event_type: Specific event type to handle, None for all events
        """

        def decorator(func: Callable):
            if event_type:
                if event_type not in self._handlers:
                    self._handlers[event_type] = []
                self._handlers[event_type].append(func)
                logger.info(
                    f"Registered handler {func.__name__} for event type: {event_type}"
                )
            else:
                self._global_handlers.append(func)
                logger.info(f"Registered global handler: {func.__name__}")
            return func

        return decorator

    def handle_event(self, event: OutboxEvent) -> bool:
        """
        Handle an event by calling registered handlers

        Args:
            event: The event to handle

        Returns:
            bool: True if all handlers succeeded, False otherwise
        """
        success = True

        # Call specific handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event)
                    logger.debug(
                        f"Handler {handler.__name__} processed event {event.id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Handler {handler.__name__} failed for event {event.id}: {str(e)}"
                    )
                    success = False

        # Call global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
                logger.debug(
                    f"Global handler {handler.__name__} processed event {event.id}"
                )
            except Exception as e:
                logger.error(
                    f"Global handler {handler.__name__} failed for event {event.id}: {str(e)}"
                )
                success = False

        return success

    def get_handlers(self, event_type: Optional[str] = None) -> List[Callable]:
        """Get registered handlers for an event type"""
        if event_type:
            return self._handlers.get(event_type, []) + self._global_handlers
        return self._global_handlers

    def clear_handlers(self, event_type: Optional[str] = None):
        """Clear handlers for an event type or all handlers"""
        if event_type:
            self._handlers.pop(event_type, None)
        else:
            self._handlers.clear()
            self._global_handlers.clear()


event_registry = EventHandlerRegistry()
