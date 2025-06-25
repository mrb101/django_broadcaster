from unittest.mock import MagicMock

import pytest

from django_broadcaster.models import OutboxEvent
from django_broadcaster.registry import EventHandlerRegistry, event_registry


class TestEventHandlerRegistry:
    """Tests for the EventHandlerRegistry class"""

    def test_register_specific_handler(self):
        """Test registering a handler for a specific event type"""
        registry = EventHandlerRegistry()

        # Define a handler function
        @registry.register(event_type="test.event")
        def test_handler(event):
            return "handled"

        # Check that the handler was registered
        assert "test.event" in registry._handlers
        assert test_handler in registry._handlers["test.event"]
        assert len(registry._global_handlers) == 0

    def test_register_global_handler(self):
        """Test registering a global handler"""
        registry = EventHandlerRegistry()

        # Define a global handler function
        @registry.register()
        def global_handler(event):
            return "handled"

        # Check that the handler was registered as a global handler
        assert len(registry._handlers) == 0
        assert global_handler in registry._global_handlers

    @pytest.mark.django_db
    def test_handle_event_specific_handler(self):
        """Test handling an event with a specific handler"""
        registry = EventHandlerRegistry()

        # Create a mock handler
        mock_handler = MagicMock()
        mock_handler.__name__ = "mock_handler"
        registry._handlers["test.event"] = [mock_handler]

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Handle the event
        result = registry.handle_event(event)

        # Check that the handler was called
        mock_handler.assert_called_once_with(event)

        # Check that the result is True (success)
        assert result is True

    @pytest.mark.django_db
    def test_handle_event_global_handler(self):
        """Test handling an event with a global handler"""
        registry = EventHandlerRegistry()

        # Create a mock global handler
        mock_global_handler = MagicMock()
        mock_global_handler.__name__ = "mock_global_handler"
        registry._global_handlers = [mock_global_handler]

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Handle the event
        result = registry.handle_event(event)

        # Check that the global handler was called
        mock_global_handler.assert_called_once_with(event)

        # Check that the result is True (success)
        assert result is True

    @pytest.mark.django_db
    def test_handle_event_both_handlers(self):
        """Test handling an event with both specific and global handlers"""
        registry = EventHandlerRegistry()

        # Create mock handlers
        mock_specific_handler = MagicMock()
        mock_specific_handler.__name__ = "mock_specific_handler"
        mock_global_handler = MagicMock()
        mock_global_handler.__name__ = "mock_global_handler"

        registry._handlers["test.event"] = [mock_specific_handler]
        registry._global_handlers = [mock_global_handler]

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Handle the event
        result = registry.handle_event(event)

        # Check that both handlers were called
        mock_specific_handler.assert_called_once_with(event)
        mock_global_handler.assert_called_once_with(event)

        # Check that the result is True (success)
        assert result is True

    @pytest.mark.django_db
    def test_handle_event_handler_exception(self):
        """Test handling an event when a handler raises an exception"""
        registry = EventHandlerRegistry()

        # Create a mock handler that raises an exception
        mock_handler = MagicMock(side_effect=Exception("Test error"))
        mock_handler.__name__ = "mock_handler_with_exception"
        registry._handlers["test.event"] = [mock_handler]

        # Create a test event
        event = OutboxEvent.objects.create(
            event_type="test.event", source="test-source"
        )

        # Handle the event
        result = registry.handle_event(event)

        # Check that the handler was called
        mock_handler.assert_called_once_with(event)

        # Check that the result is False (failure)
        assert result is False

    def test_get_handlers(self):
        """Test getting handlers for an event type"""
        registry = EventHandlerRegistry()

        # Create some handlers
        def specific_handler(event):
            pass

        def global_handler(event):
            pass

        # Register the handlers
        registry._handlers["test.event"] = [specific_handler]
        registry._global_handlers = [global_handler]

        # Get handlers for test.event
        handlers = registry.get_handlers("test.event")

        # Check that both handlers are returned
        assert specific_handler in handlers
        assert global_handler in handlers
        assert len(handlers) == 2

        # Get handlers for another event type
        handlers = registry.get_handlers("other.event")

        # Check that only global handlers are returned
        assert global_handler in handlers
        assert len(handlers) == 1

        # Get all global handlers
        handlers = registry.get_handlers()

        # Check that only global handlers are returned
        assert global_handler in handlers
        assert len(handlers) == 1

    def test_clear_handlers(self):
        """Test clearing handlers"""
        registry = EventHandlerRegistry()

        # Create some handlers
        def specific_handler1(event):
            pass

        def specific_handler2(event):
            pass

        def global_handler(event):
            pass

        # Register the handlers
        registry._handlers["test.event1"] = [specific_handler1]
        registry._handlers["test.event2"] = [specific_handler2]
        registry._global_handlers = [global_handler]

        # Clear handlers for test.event1
        registry.clear_handlers("test.event1")

        # Check that test.event1 handlers are cleared
        assert "test.event1" not in registry._handlers
        assert "test.event2" in registry._handlers
        assert len(registry._global_handlers) == 1

        # Clear all handlers
        registry.clear_handlers()

        # Check that all handlers are cleared
        assert len(registry._handlers) == 0
        assert len(registry._global_handlers) == 0

    def test_singleton_instance(self):
        """Test that event_registry is a singleton instance of EventHandlerRegistry"""
        assert isinstance(event_registry, EventHandlerRegistry)
