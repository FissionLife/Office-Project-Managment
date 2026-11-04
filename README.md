# 🤖 Office Staffing Agent-to-Agent (A2A) System

An autonomous multi-agent system designed for **Office Project Resource Allocation**. When a user submits any project proposal (software engineering, corporate events, marketing campaigns, office migrations, or compliance audits), two specialized autonomous agents communicate over a structured **Agent-to-Agent (A2A)** protocol to evaluate requirements, query employee availability, negotiate bottlenecks, and assemble the optimal cross-functional team roster.

---

## 🌟 Highlights

- **Pure Agent-to-Agent (A2A) Protocol**: Agents pass typed, auditable Pydantic messages (`A2AMessage`) containing timestamps, intent, reasoning monologues, and typed payloads.
- **Autonomous Project Classification**: Automatically classifies input projects into **Technical**, **Non-Technical**, or **Hybrid** domains.
- **Agent 1: Project & Staffing Strategist**:
  - Deduces role requirements, leadership needs, and required skill tags.
  - Negotiates candidate bandwidth with Agent 2.
  - Performs conflict detection and workload mitigation if candidates are overcommitted.
- **Agent 2: Database & Resource Specialist**:
  - Queries an SQLite database populated with 30 realistic employees (15 Tech, 15 Non-Tech/Hybrid).
  - Calculates multi-factor relevance scores based on skill overlap, available bandwidth %, and performance history.
- **Two User Interfaces Included**:
  1. **Interactive CLI** with colored, real-time message exchange traces.
  2. **Modern Web Dashboard** built with FastAPI and Tailwind CSS.
- **Fully Tested**: End-to-end test suite included with PyTest.

---

## 🏛️ System Architecture Overview

```
                      +------------------------------------------+
                      |               USER INPUT                 |
                      |  "Build AI Telemedicine Mobile App"      |
                      +--------------------+---------------------+
                                           |
                                           v
                       +---------------------------------------+
                       |               AGENT 1                 |
                       |     Project & Staffing Strategist     |
                       +-----------+-------------------^-------+
                                   |                   |
               A2A_CANDIDATE_QUERY |                   | A2A_CANDIDATE_RESPONSE
             (Role, Skills, Avail) |                   | (Ranked candidate pool)
                                   v                   |
                       +-------------------------------+-------+
                       |               AGENT 2                 |
                       |     Database & Resource Specialist    |
                       +-------------------+-------------------+
                                           |
                                           v
                               +-----------------------+
                               |      SQLITE DB        |
                               | (30 Tech & Non-Tech)  |
                               +-----------------------+
```

---

## 🚀 Quick Start with `uv`

### 1. Prerequisites
- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (Fast Python package and project manager)

Sync dependencies automatically into a local virtual environment:
```bash
uv sync
```

### 2. Run the Interactive CLI
The CLI prints the real-time A2A message exchange between Agent 1 and Agent 2:

```bash
uv run python cli.py
```

You can choose from 4 preset scenarios or enter your own custom project title and description:
- `[1]` Autonomous AI Healthcare Patient Portal *(Tech)*
- `[2]` Global Tech Leaders Annual Summit 2027 *(Non-Tech)*
- `[3]` Fintech Mobile Banking App & Nationwide Launch *(Hybrid)*
- `[4]` Corporate Office Relocation & Culture Onboarding *(Non-Tech)*
- `[5]` Custom Project *(Type any project)*

---

### 3. Launch the Web Dashboard
Launch the interactive web UI:

```bash
uv run python -m src.web.app
# OR: uv run uvicorn src.web.app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Features on the Web Dashboard:
- One-click preset chip selectors.
- Live streaming timeline of the Agent-to-Agent message transcript.
- Real-time team roster display with match percentages, roles, and individual justification badges.

---

## 🧪 Running Tests

Run the test suite with PyTest via `uv`:

```bash
uv run pytest -v
```

---

## 📂 Project Structure

```
a2a-project/
├── ARCHITECTURE.md          # Formal A2A specification and sequence diagrams
├── README.md                # Project overview and quick start guide
├── DEV.md                   # Developer guide, pruning rules, and agent extension
├── requirements.txt         # Project dependencies
├── cli.py                   # Terminal runner with colored A2A message traces
├── data/
│   └── office_management.db # SQLite database storing employees and project history
├── src/
│   ├── config.py            # Central configuration and agent identities
│   ├── db/
│   │   ├── connection.py    # SQLite connection manager
│   │   ├── init_db.py       # Seeds 30 detailed employee profiles
│   │   └── repository.py    # Multi-factor search & candidate ranking
│   ├── protocol/
│   │   ├── messages.py      # Typed A2A Pydantic message envelopes
│   │   └── bus.py           # In-memory pub/sub message broker
│   ├── agents/
│   │   ├── base.py          # Abstract BaseAgent class
│   │   ├── project_agent.py # Agent 1: Project & Staffing Strategist
│   │   └── database_agent.py# Agent 2: Database & Resource Specialist
│   ├── orchestration/
│   │   └── coordinator.py   # Runs the A2A conversation lifecycle
│   └── web/
│       ├── app.py           # FastAPI web application
│       └── templates/
│           └── index.html   # Modern responsive dashboard
└── tests/
    ├── test_db.py           # Database and repository unit tests
    ├── test_protocol.py     # Protocol serialization and pub/sub tests
    └── test_a2a_flow.py     # End-to-end A2A interaction flow tests
```
