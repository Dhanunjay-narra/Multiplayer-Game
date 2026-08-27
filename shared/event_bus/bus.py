"""High-performance Async Event Bus for decoupled domain events and pub-sub messaging."""
import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("nexus.event_bus")


class DomainEvent(BaseModel):
    """Base domain event carrying metadata and payload."""
    event_type: str
    source: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0.0)


EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class AsyncEventBus:
    """In-memory and scalable pub-sub asynchronous event dispatcher."""
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._wildcard_subscribers: List[EventHandler] = []
        self._event_history: List[DomainEvent] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribes an async handler to a specific event type."""
        if event_type == "*":
            self._wildcard_subscribers.append(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Removes a handler subscription."""
        if event_type == "*" and handler in self._wildcard_subscribers:
            self._wildcard_subscribers.remove(handler)
        elif event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publishes an event to all matching handlers concurrently."""
        self._event_history.append(event)
        # Cap event history in memory
        if len(self._event_history) > 10000:
            self._event_history = self._event_history[-5000:]

        handlers: List[EventHandler] = []
        if event.event_type in self._subscribers:
            handlers.extend(self._subscribers[event.event_type])
        handlers.extend(self._wildcard_subscribers)

        if not handlers:
            return

        tasks = [asyncio.create_task(self._safe_execute(handler, event)) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error executing event handler for {event.event_type}: {e}", exc_info=True)

    def clear_history(self) -> None:
        self._event_history.clear()


# Global Singleton instance
event_bus = AsyncEventBus()
