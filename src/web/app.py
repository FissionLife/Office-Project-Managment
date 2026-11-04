from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.orchestration.coordinator import A2ACoordinator
from src.db.repository import EmployeeRepository
from src.db.init_db import init_database

TEMPLATES_DIR = Path(__file__).parent / "templates"

class StaffingRequest(BaseModel):
    title: str
    description: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Guarantee DB exists and is seeded on startup
    init_database()
    yield

app = FastAPI(
    title="Office Management A2A Staffing Engine",
    lifespan=lifespan
)

@app.get("/", response_class=HTMLResponse)
def index_page():
    html_file = TEMPLATES_DIR / "index.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Index template not found")
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))

@app.post("/api/staff-project")
def staff_project_endpoint(request: StaffingRequest):
    if not request.title.strip():
        raise HTTPException(status_code=400, detail="Project title is required")
    coordinator = A2ACoordinator()
    result = coordinator.run_staffing_pipeline(request.title, request.description)
    return result

@app.get("/api/employees")
def list_employees():
    repo = EmployeeRepository()
    return repo.get_all_employees()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.web.app:app", host="127.0.0.1", port=8000, reload=True)
