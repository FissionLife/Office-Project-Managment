from typing import Optional, Dict, Any, List
from src.agents.base import BaseAgent
from src.protocol.messages import A2AMessage, MessageType, CandidateMatch
from src.protocol.bus import MessageBus
from src.db.repository import EmployeeRepository

class DatabaseAgent(BaseAgent):
    """
    Agent 2: Database & Resource Specialist
    Responsible for interrogating the employee database, evaluating bandwidth,
    scoring candidate relevance, and resolving staffing conflict requests.
    """

    def __init__(self, agent_id: str, name: str, bus: MessageBus, repository: Optional[EmployeeRepository] = None):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role_description="Connects to the organizational database, queries personnel skills, workload, and returns ranked candidates.",
            bus=bus
        )
        self.repository = repository or EmployeeRepository()

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Routes incoming A2A messages to the appropriate query handler."""
        if message.message_type == MessageType.A2A_CANDIDATE_QUERY:
            return self._handle_candidate_query(message)
        elif message.message_type == MessageType.A2A_CONFLICT_QUERY:
            return self._handle_conflict_query(message)
        return None

    def _handle_candidate_query(self, message: A2AMessage) -> A2AMessage:
        role_req = message.payload.get("role_requirement", {})
        role_name = role_req.get("role_name", "Unknown Role")
        category = role_req.get("category", "all")
        keywords = role_req.get("keywords", [])
        min_exp = role_req.get("min_experience_years", 1)
        min_avail = role_req.get("required_bandwidth_percent", 20)

        # Query candidates from DB
        raw_candidates = self.repository.find_candidates(
            category=category,
            keywords=keywords,
            min_availability=min_avail,
            min_experience=min_exp,
            limit=5
        )

        # Fallback: if no candidates found with strict availability, query with relaxed criteria
        fallback_used = False
        if not raw_candidates:
            fallback_used = True
            raw_candidates = self.repository.find_candidates(
                category=category,
                keywords=keywords,
                min_availability=10,
                min_experience=1,
                limit=5
            )

        candidates = [CandidateMatch(**c).model_dump() for c in raw_candidates]

        reasoning = (
            f"Searched DB for role '{role_name}' with keywords {keywords} in category '{category}'. "
            f"Found {len(candidates)} candidate(s). "
            + ("Note: Had to relax availability constraints." if fallback_used else "All candidates meet availability.")
        )

        response_payload = {
            "role_name": role_name,
            "category": category,
            "candidates_found": len(candidates),
            "candidates": candidates,
            "fallback_used": fallback_used,
            "top_pick": candidates[0] if candidates else None
        }

        return self.send_message(
            recipient=message.sender,
            message_type=MessageType.A2A_CANDIDATE_RESPONSE,
            summary=f"Found {len(candidates)} candidate(s) for '{role_name}'",
            payload=response_payload,
            reasoning=reasoning
        )

    def _handle_conflict_query(self, message: A2AMessage) -> A2AMessage:
        conflict_data = message.payload
        role_name = conflict_data.get("role_name", "")
        issue = conflict_data.get("issue", "")
        keywords = conflict_data.get("keywords", [])
        category = conflict_data.get("category", "all")

        # Search for cross-functional or high-availability alternatives
        alternatives_raw = self.repository.find_candidates(
            category="all" if category == "hybrid" else category,
            keywords=keywords,
            min_availability=70,  # Look specifically for unencumbered staff
            min_experience=2,
            limit=3
        )

        alternatives = [CandidateMatch(**c).model_dump() for c in alternatives_raw]

        reasoning = (
            f"Addressing conflict '{issue}' for role '{role_name}'. "
            f"Scanned database for high-availability (>70% bandwidth) alternatives. "
            f"Identified {len(alternatives)} alternative candidate(s)."
        )

        return self.send_message(
            recipient=message.sender,
            message_type=MessageType.A2A_CONFLICT_RESPONSE,
            summary=f"Provided {len(alternatives)} high-bandwidth alternative(s) for '{role_name}'",
            payload={
                "role_name": role_name,
                "alternatives": alternatives,
                "mitigation_advice": "Consider pairing a mid-level high-bandwidth developer with advisory hours from the senior lead."
            },
            reasoning=reasoning
        )

