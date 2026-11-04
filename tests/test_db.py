import pytest
from src.db.init_db import init_database
from src.db.repository import EmployeeRepository

@pytest.fixture(autouse=True)
def setup_db():
    init_database()

def test_get_all_employees():
    repo = EmployeeRepository()
    employees = repo.get_all_employees()
    assert len(employees) >= 30
    tech_count = sum(1 for e in employees if e["category"] == "tech")
    non_tech_count = sum(1 for e in employees if e["category"] == "non_tech")
    assert tech_count >= 14
    assert non_tech_count >= 12

def test_find_tech_candidates():
    repo = EmployeeRepository()
    candidates = repo.find_candidates(category="tech", keywords=["Python", "Backend"], limit=5)
    assert len(candidates) > 0
    top = candidates[0]
    assert "Python" in top["skills"]
    assert top["match_score"] > 60

def test_find_non_tech_candidates():
    repo = EmployeeRepository()
    candidates = repo.find_candidates(category="non_tech", keywords=["Event Planning", "Venue"], limit=5)
    assert len(candidates) > 0
    top = candidates[0]
    assert top["name"] == "Chloe Grace"
    assert top["availability_percent"] == 100

