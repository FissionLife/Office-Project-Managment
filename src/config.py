import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "office_management.db"

# Agent configuration
AGENT_PLANNER_ID = "agent_project_planner"
AGENT_PLANNER_NAME = "Project & Staffing Strategist (Agent 1)"

AGENT_DB_ID = "agent_employee_db"
AGENT_DB_NAME = "Database & Resource Specialist (Agent 2)"

