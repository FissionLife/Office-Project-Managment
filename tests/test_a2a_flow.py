from src.orchestration.coordinator import A2ACoordinator
from src.protocol.messages import MessageType

def test_tech_project_a2a_flow():
    coordinator = A2ACoordinator()
    result = coordinator.run_staffing_pipeline(
        title="Scalable Microservices Gateway",
        description="Build a high performance Python and Go microservices backend with Docker and Kubernetes deployment."
    )

    assert result["category"] == "tech"
    decision = result["decision"]
    assert decision["team_size"] >= 4
    assert len(result["a2a_transcript"]) >= 8

    # Verify message flow contains expected message types
    types = [m["message_type"] for m in result["a2a_transcript"]]
    assert MessageType.PROJECT_ANALYSIS_REQUEST in types
    assert MessageType.A2A_CANDIDATE_QUERY in types
    assert MessageType.A2A_CANDIDATE_RESPONSE in types
    assert MessageType.FINAL_ROSTER_DECISION in types

def test_non_tech_project_a2a_flow():
    coordinator = A2ACoordinator()
    result = coordinator.run_staffing_pipeline(
        title="Annual PR & Brand Gala",
        description="Organize an international corporate gala, press outreach, influencer campaign, and vendor contracts."
    )

    assert result["category"] == "non_tech"
    decision = result["decision"]
    assert decision["team_size"] >= 4

    roles = [m["assigned_role"] for m in decision["team_roster"]]
    # Should include events or marketing or PR roles
    assert any("Event" in r or "Marketing" in r or "PR" in r or "Brand" in r for r in roles)

