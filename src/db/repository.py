import json
import sqlite3
from typing import List, Dict, Any, Optional
from src.db.connection import get_connection

class EmployeeRepository:
    """Provides structured data query and matching capabilities over the employee database."""

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self._external_conn = conn

    def _get_conn(self) -> sqlite3.Connection:
        if self._external_conn:
            return self._external_conn
        return get_connection()

    def get_all_employees(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees ORDER BY category, role")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        finally:
            if not self._external_conn:
                conn.close()

    def find_candidates(
        self,
        category: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        min_availability: int = 20,
        min_experience: int = 1,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Searches employees matching category, keywords (in role, skills, bio),
        and availability filters.
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM employees WHERE availability_percent >= ? AND years_experience >= ?"
            params: List[Any] = [min_availability, min_experience]

            if category and category != "all":
                if category == "tech":
                    query += " AND category IN ('tech', 'hybrid')"
                elif category == "non_tech":
                    query += " AND category IN ('non_tech', 'hybrid')"
                else:
                    query += " AND category = ?"
                    params.append(category)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            candidates = [self._row_to_dict(r) for r in rows]

            # If keywords were provided, score and rank them
            if keywords:
                lower_keywords = [kw.lower() for kw in keywords if kw]
                scored = []
                for cand in candidates:
                    score = self._compute_relevance_score(cand, lower_keywords)
                    cand["match_score"] = round(score, 2)
                    scored.append((score, cand))
                
                # Sort by score descending, then availability descending
                scored.sort(key=lambda x: (x[0], x[1]["availability_percent"]), reverse=True)
                return [item[1] for item in scored[:limit]]
            else:
                for c in candidates:
                    c["match_score"] = 50.0  # baseline
                candidates.sort(key=lambda x: (x["availability_percent"], x["performance_rating"]), reverse=True)
                return candidates[:limit]

        finally:
            if not self._external_conn:
                conn.close()

    def _compute_relevance_score(self, emp: Dict[str, Any], keywords: List[str]) -> float:
        """
        Computes a 0-100 score based on keyword match, availability, and rating.
        - Keyword overlap: up to 50 pts
        - Availability: up to 30 pts (pro-rated from availability_percent)
        - Performance & Experience: up to 20 pts
        """
        skills_text = " ".join(emp.get("skills", [])).lower()
        role_text = emp.get("role", "").lower()
        dept_text = emp.get("department", "").lower()
        bio_text = emp.get("bio", "").lower()

        matched_kw_count = 0
        for kw in keywords:
            if kw in skills_text or kw in role_text or kw in dept_text or kw in bio_text:
                matched_kw_count += 1

        keyword_ratio = (matched_kw_count / len(keywords)) if keywords else 0.5
        kw_points = min(50.0, keyword_ratio * 50.0)

        # Availability (0-30 pts)
        avail = emp.get("availability_percent", 0)
        avail_points = (avail / 100.0) * 30.0

        # Performance (0-10 pts) and Experience (0-10 pts)
        rating = emp.get("performance_rating", 3.0)
        perf_points = (rating / 5.0) * 10.0
        exp = emp.get("years_experience", 1)
        exp_points = min(10.0, (exp / 10.0) * 10.0)

        total = kw_points + avail_points + perf_points + exp_points
        return round(total, 1)

    def save_project_history(self, title: str, category: str, description: str, roster: List[Dict[str, Any]]) -> int:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO project_history (title, category, description, roster_json)
                VALUES (?, ?, ?, ?)
            """, (title, category, description, json.dumps(roster)))
            conn.commit()
            return cursor.lastrowid
        finally:
            if not self._external_conn:
                conn.close()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        if isinstance(data.get("skills"), str):
            try:
                data["skills"] = json.loads(data["skills"])
            except Exception:
                data["skills"] = [s.strip() for s in data["skills"].split(",")]
        if isinstance(data.get("current_projects"), str):
            try:
                data["current_projects"] = json.loads(data["current_projects"])
            except Exception:
                data["current_projects"] = []
        return data

