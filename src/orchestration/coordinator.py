from typing import Dict, Any, List
from src.protocol.bus import MessageBus
from src.protocol.messages import A2AMessage
from src.agents.database_agent import DatabaseAgent
from src.agents.project_agent import ProjectStaffingAgent
from src.db.repository import EmployeeRepository
from src.config import AGENT_PLANNER_ID, AGENT_PLANNER_NAME, AGENT_DB_ID, AGENT_DB_NAME

class A2ACoordinator:
    """
    Coordinates and hosts the A2A runtime between:
    - Agent 1: Project & Staffing Strategist
    - Agent 2: Database & Resource Specialist
    """

    def __init__(self):
        self.bus = MessageBus()
        self.repo = EmployeeRepository()
        self.db_agent = DatabaseAgent(
            agent_id=AGENT_DB_ID,
            name=AGENT_DB_NAME,
            bus=self.bus,
            repository=self.repo
        )
        self.planner_agent = ProjectStaffingAgent(
            agent_id=AGENT_PLANNER_ID,
            name=AGENT_PLANNER_NAME,
            bus=self.bus,
            db_agent_id=AGENT_DB_ID
        )

    def run_staffing_pipeline(self, title: str, description: str) -> Dict[str, Any]:
        """Runs the complete collaborative A2A loop."""
        self.bus.clear()

        # Execute Agent 1's staffing and negotiation flow
        decision = self.planner_agent.plan_and_staff_project(title, description)

        # Save result to database project history
        roster = decision.get("team_roster", [])
        category = decision.get("project_category", "general")
        self.repo.save_project_history(title, category, description, roster)

        transcript = [msg.model_dump() for msg in self.bus.get_history()]

        return {
            "title": title,
            "description": description,
            "category": category,
            "decision": decision,
            "a2a_transcript": transcript,
            "total_messages_exchanged": len(transcript)
        }

