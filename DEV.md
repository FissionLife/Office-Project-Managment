# Developer Guide & Pruning Guidelines (DEV.md)

This document provides developer operational standards, codebase maintenance procedures, instructions on how to prune/clean the project, and patterns for extending the Agent-to-Agent (A2A) network.

---

## 1. Development Setup with `uv`

The project uses [`uv`](https://docs.astral.sh/uv/) for high-performance dependency management and virtual environments via `pyproject.toml`.

### Sync Dependencies
```bash
uv sync
```

### Running Unit & Integration Tests
```bash
uv run pytest -v
```

### Running the App
```bash
# Terminal Runner (CLI)
uv run python cli.py

# Web Dashboard (FastAPI)
uv run python -m src.web.app
```

---

## 2. Pruning & Maintenance Procedures

When preparing this project for production, archiving, or lightweight containerization, execute the following pruning steps:

### A. Prune Python Cache & Test Artifacts
Remove all `.pytest_cache` and `__pycache__` directories to keep the workspace clean:
```powershell
# PowerShell:
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter ".pytest_cache" | Remove-Item -Recurse -Force
```

### B. Prune Database & Reset Seed Data
To purge all historical projects and reset the employee database to factory default:
```powershell
# Delete the SQLite database file
Remove-Item -Path "data\office_management.db" -Force

# Re-initialize the database with seed records
uv run python -m src.db.init_db
```

### C. Prune In-Memory Message History
In high-throughput environments, `MessageBus.history` can accumulate messages indefinitely. Use `coordinator.bus.clear()` between runs or implement a capped FIFO ring buffer (e.g., `collections.deque(maxlen=1000)`).

---

## 3. Extending the A2A Network

The system is built on an open agent contract: any agent inheriting from `BaseAgent` can participate in the protocol.

### Example: Adding a 3rd Agent ("Budget & Financial Auditor Agent")

To add an agent that verifies whether proposed staffing exceeds a project's budget cap:

1. **Define the Message Type in `src/protocol/messages.py`**:
   ```python
   class MessageType(str, Enum):
       ...
       A2A_BUDGET_AUDIT_QUERY = "A2A_BUDGET_AUDIT_QUERY"
       A2A_BUDGET_AUDIT_RESPONSE = "A2A_BUDGET_AUDIT_RESPONSE"
   ```

2. **Create the Agent in `src/agents/budget_agent.py`**:
   ```python
   from src.agents.base import BaseAgent
   from src.protocol.messages import A2AMessage, MessageType

   class BudgetAuditorAgent(BaseAgent):
       def __init__(self, bus):
           super().__init__(
               agent_id="agent_budget_auditor",
               name="Budget & Compliance Auditor (Agent 3)",
               role_description="Audits team payroll rates and verifies project cost limits.",
               bus=bus
           )

       def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
           if message.message_type == MessageType.A2A_BUDGET_AUDIT_QUERY:
               roster = message.payload.get("roster", [])
               # Perform cost calculation
               is_approved = len(roster) <= 10
               return self.send_message(
                   recipient=message.sender,
                   message_type=MessageType.A2A_BUDGET_AUDIT_RESPONSE,
                   summary="Budget approved" if is_approved else "Budget exceeded",
                   payload={"approved": is_approved, "projected_cost": len(roster) * 15000}
               )
           return None
   ```

3. **Register in `A2ACoordinator` (`src/orchestration/coordinator.py`)**:
   Add the new agent to the coordinator and invoke its query before generating the `FINAL_ROSTER_DECISION`.

---

## 4. Connecting External LLMs (Gemini / OpenAI / Anthropic)

The heuristic decision logic in `src/agents/project_agent.py` can be seamlessly substituted or augmented with LLM tool-calling:

```python
import os
import google.generativeai as genai

class ProjectStaffingAgent(BaseAgent):
    def __init__(self, ...):
        ...
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    def _classify_project(self, title: str, description: str):
        if self.model:
            prompt = f"Classify this project as 'tech', 'non_tech', or 'hybrid': {title} - {description}"
            response = self.model.generate_content(prompt)
            # Parse classification...
        else:
            # Fallback to local heuristic classifier
            return super()._classify_project(title, description)
```

---

## 5. Coding Standards & Conventions

- **Typing**: Use standard Python type hints (`from typing import Optional, List, Dict, Any`).
- **Data Validation**: Keep all A2A network payloads validated via Pydantic (`BaseModel`).
- **Database Safety**: Never interpolate raw strings into SQL queries. Always use parameterized queries (`?`).
- **Encoding**: Consistently use `utf-8` file reads and writes across both Windows and Unix operating environments.
