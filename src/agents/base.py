from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.protocol.messages import A2AMessage, MessageType
from src.protocol.bus import MessageBus

class BaseAgent(ABC):
    """Abstract Base Class for autonomous agents participating in A2A protocols."""

    def __init__(self, agent_id: str, name: str, role_description: str, bus: MessageBus):
        self.agent_id = agent_id
        self.name = name
        self.role_description = role_description
        self.bus = bus

    def send_message(
        self,
        recipient: str,
        message_type: MessageType,
        summary: str,
        payload: Dict[str, Any],
        reasoning: Optional[str] = None
    ) -> A2AMessage:
        """Constructs an A2AMessage and publishes it to the shared MessageBus."""
        msg = A2AMessage(
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            summary=summary,
            payload=payload,
            reasoning=reasoning
        )
        return self.bus.publish(msg)

    @abstractmethod
    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Process an incoming message and optionally return a direct response."""
        pass

