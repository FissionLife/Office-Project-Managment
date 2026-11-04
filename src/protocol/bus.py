from typing import List, Callable, Dict, Any
from src.protocol.messages import A2AMessage

class MessageBus:
    """A2A Event Bus handling message routing, history logging, and live event callbacks."""

    def __init__(self):
        self.history: List[A2AMessage] = []
        self._subscribers: List[Callable[[A2AMessage], None]] = []

    def subscribe(self, callback: Callable[[A2AMessage], None]) -> None:
        """Register a callback for real-time message stream notifications."""
        self._subscribers.append(callback)

    def publish(self, message: A2AMessage) -> A2AMessage:
        """Publishes a message into history and notifies subscribers."""
        self.history.append(message)
        for sub in self._subscribers:
            try:
                sub(message)
            except Exception as e:
                print(f"[MessageBus Warning] Callback error: {e}")
        return message

    def get_history(self) -> List[A2AMessage]:
        return list(self.history)

    def clear(self) -> None:
        self.history.clear()

