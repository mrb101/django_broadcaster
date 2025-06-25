import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import redis

from django_broadcaster.models import OutboxEvent

logger = logging.getLogger(__name__)


class PublisherBackend(ABC):
    """
    Abstract base class for publisher backends
    """

    @abstractmethod
    def publish(self, event: OutboxEvent) -> bool:
        """
        Publish an event to the backend

        Args:
            event: The OutboxEvent to publish

        Returns:
            bool: True if successful, False otherwise

        Raises:
            Exception: If publishing fails
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the backend is healthy and available

        Returns:
            bool: True if healthy, False otherwise
        """
        pass

    def get_name(self) -> str:
        """Get the backend name"""
        return self.__class__.__name__


class RedisStreamBackend(PublisherBackend):
    """
    Redis Stream publisher backend
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("host", "localhost"),
            port=config.get("port", 6379),
            db=config.get("db", 0),
            password=config.get("password"),
            decode_responses=True,
            socket_connect_timeout=config.get("connect_timeout", 5),
            socket_timeout=config.get("socket_timeout", 5),
            health_check_interval=30,
        )
        self.stream_name = config.get("stream_name", "events")
        self.max_len = config.get("max_len", 10000)

    def publish(self, event: OutboxEvent) -> bool:
        """
        Publish event to Redis Stream
        """
        try:
            cloud_event = event.to_cloud_event()

            # Add event metadata
            stream_data = {
                "event_id": str(event.id),
                "event_type": event.event_type,
                "source": event.source,
                "timestamp": event.created_at.isoformat(),
                "cloud_event": json.dumps(cloud_event),
            }

            # Add custom fields if configured
            if event.publisher_config:
                stream_data.update(event.publisher_config)

            # Publish to Redis Stream
            message_id = self.redis_client.xadd(
                self.stream_name, stream_data, maxlen=self.max_len, approximate=True
            )

            logger.info(
                f"Published event {event.id} to Redis Stream with message ID: {message_id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to publish event {event.id} to Redis Stream: {str(e)}"
            )
            raise

    def health_check(self) -> bool:
        """
        Check Redis connection health
        """
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False

    def get_name(self) -> str:
        return "RedisStream"
