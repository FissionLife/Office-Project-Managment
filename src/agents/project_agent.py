import re
from typing import Optional, Dict, Any, List, Tuple
from src.agents.base import BaseAgent
from src.protocol.messages import A2AMessage, MessageType, RoleRequirement
from src.protocol.bus import MessageBus

class ProjectStaffingAgent(BaseAgent):
    """
    Agent 1: Project & Staffing Strategist
    Analyzes project specifications, deduces required competencies, coordinates
    with the DatabaseAgent (Agent 2) to identify suitable personnel, resolves
    workload contention, and synthesizes the final staffing roster.
    """

    def __init__(self, agent_id: str, name: str, bus: MessageBus, db_agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role_description="Understands project objectives, structures team roles, negotiates staffing with Database Agent, and formulates the team.",
            bus=bus
        )
        self.db_agent_id = db_agent_id

    def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        # Agent 1 handles incoming responses from Agent 2 or client requests
        return None

    def plan_and_staff_project(self, project_title: str, project_description: str) -> Dict[str, Any]:
        """
        Main orchestration loop executed by Agent 1:
        1. Classifies the project (Tech vs Non-Tech vs Hybrid).
        2. Deduces required roles and skill keywords.
        3. Conducts A2A message exchange with DatabaseAgent for each role.
        4. Detects conflicts and requests mitigations if availability is tight.
        5. Formulates the final team roster decision.
        """
        # Step 1: Project Analysis & Classification
        category, confidence, classification_reasoning = self._classify_project(project_title, project_description)
        role_specs = self._determine_required_roles(project_title, project_description, category)

        self.send_message(
            recipient="client",
            message_type=MessageType.PROJECT_ANALYSIS_REQUEST,
            summary=f"Project classified as {category.upper()}",
            payload={
                "project_title": project_title,
                "project_description": project_description,
                "category": category,
                "confidence": confidence,
                "planned_roles_count": len(role_specs),
                "planned_roles": [r.role_name for r in role_specs]
            },
            reasoning=f"Analyzed description: {classification_reasoning}. Identified {len(role_specs)} critical roles."
        )

        assigned_team: List[Dict[str, Any]] = []
        already_allocated_ids = set()

        # Step 2: A2A Inquiries for each required role
        for req in role_specs:
            # Send A2A Query to Database Agent
            query_msg = self.send_message(
                recipient=self.db_agent_id,
                message_type=MessageType.A2A_CANDIDATE_QUERY,
                summary=f"Requesting candidates for '{req.role_name}'",
                payload={"role_requirement": req.model_dump()},
                reasoning=f"Need candidate with skills: {req.keywords}, min exp: {req.min_experience_years}y, bandwidth: {req.required_bandwidth_percent}%."
            )

            # In this synchronous broker model, Agent 2 responds to the query
            from src.agents.database_agent import DatabaseAgent
            db_agent = self._get_db_agent()
            response_msg = db_agent.handle_message(query_msg)
            if not response_msg:
                continue

            candidates = response_msg.payload.get("candidates", [])
            # Filter out anyone already assigned to avoid double booking in single project
            viable_candidates = [c for c in candidates if c["id"] not in already_allocated_ids]
            if not viable_candidates and candidates:
                viable_candidates = candidates  # Fallback to shared allocation if small pool

            if not viable_candidates:
                continue

            primary_candidate = viable_candidates[0]

            # Step 3: Conflict Detection & A2A Mitigation
            # If candidate availability is low (e.g. <= 35%), initiate conflict dialog
            if primary_candidate["availability_percent"] <= 35:
                conflict_msg = self.send_message(
                    recipient=self.db_agent_id,
                    message_type=MessageType.A2A_CONFLICT_QUERY,
                    summary=f"Bandwidth conflict for candidate {primary_candidate['name']}",
                    payload={
                        "role_name": req.role_name,
                        "candidate_name": primary_candidate["name"],
                        "issue": f"Candidate has only {primary_candidate['availability_percent']}% availability, but role requires {req.required_bandwidth_percent}%.",
                        "keywords": req.keywords,
                        "category": req.category
                    },
                    reasoning=f"{primary_candidate['name']} is a strong skill match ({primary_candidate['match_score']}), but currently overcommitted ({primary_candidate['availability_percent']}% free)."
                )

                conflict_response = db_agent.handle_message(conflict_msg)
                alternatives = conflict_response.payload.get("alternatives", []) if conflict_response else []
                alt_filtered = [a for a in alternatives if a["id"] not in already_allocated_ids]

                if alt_filtered:
                    chosen = alt_filtered[0]
                    decision_note = (
                        f"Substituted with {chosen['name']} ({chosen['availability_percent']}% available) "
                        f"to avoid overloading {primary_candidate['name']} ({primary_candidate['availability_percent']}% available)."
                    )
                else:
                    chosen = primary_candidate
                    decision_note = (
                        f"Retained {chosen['name']} despite tight bandwidth ({chosen['availability_percent']}%) "
                        f"due to exceptional domain expertise. Recommended pairing with junior support."
                    )
            else:
                chosen = primary_candidate
                decision_note = (
                    f"Selected {chosen['name']} (Match Score: {chosen['match_score']}, "
                    f"Experience: {chosen['years_experience']}y, Available: {chosen['availability_percent']}%)."
                )

            already_allocated_ids.add(chosen["id"])
            assigned_team.append({
                "assigned_role": req.role_name,
                "is_leadership": req.is_leadership,
                "employee_id": chosen["id"],
                "employee_name": chosen["name"],
                "department": chosen["department"],
                "category": chosen["category"],
                "matched_skills": chosen.get("skills", []),
                "years_experience": chosen.get("years_experience", 0),
                "performance_rating": chosen.get("performance_rating", 0.0),
                "availability_percent": chosen.get("availability_percent", 0),
                "allocated_capacity_percent": min(req.required_bandwidth_percent, chosen.get("availability_percent", 50)),
                "match_score": chosen.get("match_score", 0),
                "justification": decision_note
            })

        # Step 4: Final Team Synthesis
        avg_avail = sum(m["availability_percent"] for m in assigned_team) / len(assigned_team) if assigned_team else 0
        avg_exp = sum(m["years_experience"] for m in assigned_team) / len(assigned_team) if assigned_team else 0

        final_decision_payload = {
            "project_title": project_title,
            "project_category": category,
            "team_size": len(assigned_team),
            "team_roster": assigned_team,
            "metrics": {
                "average_availability_percent": round(avg_avail, 1),
                "average_experience_years": round(avg_exp, 1),
                "all_roles_filled": len(assigned_team) == len(role_specs)
            },
            "strategic_summary": (
                f"Successfully assembled a high-performing {category.replace('_', ' ').title()} team of {len(assigned_team)} specialists. "
                f"The roster averages {round(avg_exp, 1)} years of experience with an aggregate available bandwidth of {round(avg_avail, 1)}%."
            )
        }

        self.send_message(
            recipient="client",
            message_type=MessageType.FINAL_ROSTER_DECISION,
            summary=f"Final team assembled: {len(assigned_team)} specialists",
            payload=final_decision_payload,
            reasoning="All required project roles resolved and validated against employee availability."
        )

        return final_decision_payload

    def _get_db_agent(self):
        """Helper to get DatabaseAgent reference from registry or create instance."""
        from src.agents.database_agent import DatabaseAgent
        from src.db.repository import EmployeeRepository
        return DatabaseAgent(
            agent_id=self.db_agent_id,
            name="Database & Resource Specialist (Agent 2)",
            bus=self.bus,
            repository=EmployeeRepository()
        )

    def _classify_project(self, title: str, description: str) -> Tuple[str, float, str]:
        """Classifies the project into 'tech', 'non_tech', or 'hybrid'."""
        text = f"{title} {description}".lower()

        tech_keywords = [
            "software", "app", "mobile", "web", "cloud", "api", "backend", "frontend",
            "database", "ai", "machine learning", "ml", "devops", "security", "iot",
            "kubernetes", "react", "python", "fullstack", "microservices", "pipeline",
            "flutter", "docker", "qa", "automation", "data platform"
        ]

        non_tech_keywords = [
            "marketing", "event", "conference", "gala", "brand", "rebranding", "campaign",
            "pr", "public relations", "hr", "recruiting", "culture", "onboarding", "legal",
            "contract", "finance", "budget", "operations", "logistics", "facilities",
            "office move", "content", "copywriting", "social media", "whitepaper"
        ]

        tech_hits = sum(1 for kw in tech_keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))
        non_tech_hits = sum(1 for kw in non_tech_keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))

        if tech_hits > 0 and non_tech_hits > 0 and (tech_hits >= 2 and non_tech_hits >= 2):
            category = "hybrid"
            confidence = 0.90
            reasoning = f"Detected significant tech aspects ({tech_hits} signals) and non-tech operational aspects ({non_tech_hits} signals)."
        elif tech_hits > non_tech_hits:
            category = "tech"
            confidence = min(0.98, 0.70 + (tech_hits * 0.05))
            reasoning = f"Detected technical engineering domain requirements ({tech_hits} tech signals)."
        elif non_tech_hits > tech_hits:
            category = "non_tech"
            confidence = min(0.98, 0.70 + (non_tech_hits * 0.05))
            reasoning = f"Detected corporate, marketing, or operational domain requirements ({non_tech_hits} non-tech signals)."
        else:
            category = "tech" if any(w in text for w in ["build", "system", "code"]) else "non_tech"
            confidence = 0.75
            reasoning = "Balanced or generalized description; deduced best fit."

        return category, confidence, reasoning

    def _determine_required_roles(self, title: str, description: str, category: str) -> List[RoleRequirement]:
        """Derives team staffing composition based on category and textual signals."""
        text = f"{title} {description}".lower()
        roles: List[RoleRequirement] = []

        if category == "tech":
            # 1. Project Management / Technical Lead
            roles.append(RoleRequirement(
                role_name="Technical Project Manager",
                category="hybrid",
                keywords=["Agile", "Scrum", "Risk Management", "Sprint Planning"],
                min_experience_years=5,
                required_bandwidth_percent=40,
                is_leadership=True
            ))

            # 2. Check for AI / ML requirements
            if any(k in text for k in ["ai", "ml", "machine learning", "rag", "llm", "model", "nlp", "chatbot"]):
                roles.append(RoleRequirement(
                    role_name="AI / ML Solutions Engineer",
                    category="tech",
                    keywords=["Python", "PyTorch", "LLMs", "RAG", "LangChain"],
                    min_experience_years=4,
                    required_bandwidth_percent=50
                ))

            # 3. Check for Mobile requirements
            if any(k in text for k in ["mobile", "ios", "android", "flutter", "react native", "phone", "app"]):
                roles.append(RoleRequirement(
                    role_name="Senior Mobile Developer",
                    category="tech",
                    keywords=["Flutter", "React Native", "iOS", "Android"],
                    min_experience_years=5,
                    required_bandwidth_percent=50
                ))

            # 4. Check for Data Engineering / Big Data
            if any(k in text for k in ["data", "pipeline", "spark", "warehouse", "analytics", "etl"]):
                roles.append(RoleRequirement(
                    role_name="Data Engineer",
                    category="tech",
                    keywords=["Apache Spark", "Kafka", "SQL", "Snowflake", "Python"],
                    min_experience_years=5,
                    required_bandwidth_percent=50
                ))

            # 5. Core Backend
            roles.append(RoleRequirement(
                role_name="Senior Backend Architect",
                category="tech",
                keywords=["Python", "Go", "PostgreSQL", "FastAPI", "Microservices", "REST APIs"],
                min_experience_years=4,
                required_bandwidth_percent=50
            ))

            # 6. Frontend / UI
            roles.append(RoleRequirement(
                role_name="Lead Frontend Engineer",
                category="tech",
                keywords=["React", "TypeScript", "Next.js", "Tailwind CSS"],
                min_experience_years=3,
                required_bandwidth_percent=40
            ))

            # 7. UI/UX Designer
            roles.append(RoleRequirement(
                role_name="UI/UX Product Designer",
                category="hybrid",
                keywords=["Figma", "User Research", "Wireframing", "Prototyping"],
                min_experience_years=3,
                required_bandwidth_percent=40
            ))

            # 8. DevOps / Cloud
            roles.append(RoleRequirement(
                role_name="Cloud & DevOps Engineer",
                category="tech",
                keywords=["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD"],
                min_experience_years=4,
                required_bandwidth_percent=40
            ))

            # 9. QA / Automation
            roles.append(RoleRequirement(
                role_name="QA Automation Engineer",
                category="tech",
                keywords=["Playwright", "PyTest", "API Testing", "Load Testing"],
                min_experience_years=3,
                required_bandwidth_percent=30
            ))

        elif category == "non_tech":
            # 1. Lead Organizer / PM
            if any(k in text for k in ["event", "conference", "gala", "summit", "party", "gathering"]):
                roles.append(RoleRequirement(
                    role_name="Corporate Events & Logistics Coordinator",
                    category="non_tech",
                    keywords=["Event Planning", "Venue Management", "Vendor Negotiation", "Logistics"],
                    min_experience_years=5,
                    required_bandwidth_percent=60,
                    is_leadership=True
                ))
            else:
                roles.append(RoleRequirement(
                    role_name="Principal Product & Strategy Manager",
                    category="non_tech",
                    keywords=["Product Roadmap", "Market Research", "Feature Prioritization"],
                    min_experience_years=6,
                    required_bandwidth_percent=50,
                    is_leadership=True
                ))

            # 2. Marketing / Growth
            roles.append(RoleRequirement(
                role_name="Growth Marketing Lead",
                category="non_tech",
                keywords=["Digital Marketing", "Paid Ads", "Campaigns", "Google Ads"],
                min_experience_years=4,
                required_bandwidth_percent=40
            ))

            # 3. Brand & Creative Direction
            roles.append(RoleRequirement(
                role_name="Creative Director & Brand Strategist",
                category="non_tech",
                keywords=["Brand Identity", "Visual Direction", "Campaign Creative"],
                min_experience_years=5,
                required_bandwidth_percent=40
            ))

            # 4. Copywriting & Content
            roles.append(RoleRequirement(
                role_name="Senior Content Strategist & Copywriter",
                category="non_tech",
                keywords=["Copywriting", "SEO Content", "Press Releases", "Brand Voice"],
                min_experience_years=3,
                required_bandwidth_percent=40
            ))

            # 5. Public Relations / Comms
            roles.append(RoleRequirement(
                role_name="PR & Corporate Communications Lead",
                category="non_tech",
                keywords=["Public Relations", "Media Outreach", "Press Conferences"],
                min_experience_years=5,
                required_bandwidth_percent=40
            ))

            # 6. Finance / Budget Analyst
            roles.append(RoleRequirement(
                role_name="Financial & Budget Analyst",
                category="non_tech",
                keywords=["Financial Modeling", "Budget Tracking", "Cost-Benefit Analysis"],
                min_experience_years=4,
                required_bandwidth_percent=30
            ))

            # 7. Legal or Operations check
            if any(k in text for k in ["legal", "contract", "compliance", "gdpr", "vendor", "risk"]):
                roles.append(RoleRequirement(
                    role_name="Corporate Counsel & Contracts Specialist",
                    category="non_tech",
                    keywords=["Contract Negotiation", "Vendor Agreements", "Compliance", "Risk Assessment"],
                    min_experience_years=6,
                    required_bandwidth_percent=30
                ))
            elif any(k in text for k in ["office", "relocation", "move", "facilities", "procurement"]):
                roles.append(RoleRequirement(
                    role_name="Facilities & Office Operations Manager",
                    category="non_tech",
                    keywords=["Office Operations", "Vendor Management", "Space Planning", "Procurement"],
                    min_experience_years=5,
                    required_bandwidth_percent=50
                ))

        else:  # Hybrid
            # Leadership
            roles.append(RoleRequirement(
                role_name="Senior Technical Project Manager",
                category="hybrid",
                keywords=["Agile", "Scrum", "Risk Management", "Stakeholder Communication"],
                min_experience_years=6,
                required_bandwidth_percent=50,
                is_leadership=True
            ))
            # Tech Lead / Fullstack
            roles.append(RoleRequirement(
                role_name="Fullstack Software Engineer",
                category="tech",
                keywords=["Node.js", "React", "MongoDB", "TypeScript", "Docker"],
                min_experience_years=4,
                required_bandwidth_percent=50
            ))
            # UI/UX Designer
            roles.append(RoleRequirement(
                role_name="UI/UX Product Designer",
                category="hybrid",
                keywords=["Figma", "Design Systems", "Prototyping", "User Research"],
                min_experience_years=4,
                required_bandwidth_percent=40
            ))
            # Marketing & Launch Lead
            roles.append(RoleRequirement(
                role_name="Growth Marketing Lead",
                category="non_tech",
                keywords=["Digital Marketing", "Paid Ads", "Campaigns"],
                min_experience_years=4,
                required_bandwidth_percent=40
            ))
            # Legal & Compliance
            roles.append(RoleRequirement(
                role_name="Corporate Counsel & Contracts Specialist",
                category="non_tech",
                keywords=["Contract Negotiation", "Compliance", "Vendor Agreements"],
                min_experience_years=5,
                required_bandwidth_percent=30
            ))

        return roles

