from src.protocol.messages import A2AMessage, MessageType
from src.protocol.bus import MessageBus

def test_message_creation_and_serialization():
    msg = A2AMessage(
        sender="agent_a",
        recipient="agent_b",
        message_type=MessageType.A2A_CANDIDATE_QUERY,
        summary="Looking for backend engineer",
        payload={"role": "Backend", "min_exp": 3},
        reasoning="Project needs strong database skill"
    )
    dumped = msg.model_dump()
    assert dumped["sender"] == "agent_a"
    assert dumped["recipient"] == "agent_b"
    assert dumped["message_type"] == MessageType.A2A_CANDIDATE_QUERY
    assert dumped["payload"]["role"] == "Backend"

def test_message_bus_pub_sub():
    bus = MessageBus()
    received = []

    def subscriber(m):
        received.append(m)

    bus.subscribe(subscriber)

    msg = A2AMessage(
        sender="agent_1",
        recipient="agent_2",
        message_type=MessageType.FINAL_ROSTER_DECISION,
        summary="Team complete"
    )

    published = bus.publish(msg)
    assert len(bus.get_history()) == 1
    assert len(received) == 1
    assert received[0].id == published.id

