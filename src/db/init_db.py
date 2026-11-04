import json
import sqlite3
from src.db.connection import get_connection

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('tech', 'non_tech', 'hybrid')),
    skills TEXT NOT NULL, -- JSON array of strings
    years_experience INTEGER NOT NULL,
    availability_percent INTEGER NOT NULL CHECK(availability_percent BETWEEN 0 AND 100),
    performance_rating REAL NOT NULL CHECK(performance_rating BETWEEN 1.0 AND 5.0),
    current_projects TEXT DEFAULT '[]', -- JSON array of current project titles
    bio TEXT
);

CREATE TABLE IF NOT EXISTS project_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    roster_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_employees_category ON employees(category);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_avail ON employees(availability_percent);
"""

SAMPLE_EMPLOYEES = [
    # ----------------- TECHNICAL EMPLOYEES (15) -----------------
    {
        "name": "Alice Chen",
        "email": "alice.chen@company.com",
        "department": "Engineering",
        "role": "Senior Backend Architect",
        "category": "tech",
        "skills": json.dumps(["Python", "Go", "Distributed Systems", "PostgreSQL", "FastAPI", "Microservices"]),
        "years_experience": 9,
        "availability_percent": 80,
        "performance_rating": 4.9,
        "current_projects": json.dumps(["Legacy Migration"]),
        "bio": "Expert in high-throughput backend services, distributed data pipelines, and scalable APIs."
    },
    {
        "name": "Bob Miller",
        "email": "bob.miller@company.com",
        "department": "Engineering",
        "role": "Lead Frontend Engineer",
        "category": "tech",
        "skills": json.dumps(["React", "TypeScript", "Next.js", "Tailwind CSS", "GraphQL", "Web Vitals"]),
        "years_experience": 8,
        "availability_percent": 30,
        "performance_rating": 4.8,
        "current_projects": json.dumps(["Customer Portal Redesign", "Checkout Service"]),
        "bio": "UI architecture specialist with a heavy focus on responsive web apps, state management, and modern component systems."
    },
    {
        "name": "Carlos Santana",
        "email": "carlos.santana@company.com",
        "department": "Engineering",
        "role": "Fullstack Software Engineer",
        "category": "tech",
        "skills": json.dumps(["Node.js", "React", "MongoDB", "Express", "TypeScript", "Docker"]),
        "years_experience": 5,
        "availability_percent": 100,
        "performance_rating": 4.6,
        "current_projects": json.dumps([]),
        "bio": "Versatile fullstack developer capable of rapid end-to-end MVP prototyping."
    },
    {
        "name": "Diana Prince",
        "email": "diana.prince@company.com",
        "department": "Mobile Engineering",
        "role": "Senior Mobile Developer",
        "category": "tech",
        "skills": json.dumps(["Flutter", "React Native", "iOS", "Android", "Swift", "Kotlin"]),
        "years_experience": 7,
        "availability_percent": 90,
        "performance_rating": 4.9,
        "current_projects": json.dumps([]),
        "bio": "Cross-platform and native mobile app expert with multiple published enterprise applications."
    },
    {
        "name": "Evan Wright",
        "email": "evan.wright@company.com",
        "department": "Infrastructure & Cloud",
        "role": "Cloud & DevOps Architect",
        "category": "tech",
        "skills": json.dumps(["AWS", "Kubernetes", "Terraform", "Docker", "CI/CD", "Linux", "GCP"]),
        "years_experience": 10,
        "availability_percent": 60,
        "performance_rating": 4.9,
        "current_projects": json.dumps(["Kubernetes Cluster Upgrades"]),
        "bio": "Specializes in secure cloud infrastructure, automated GitOps pipelines, and cost optimization."
    },
    {
        "name": "Fiona Gallagher",
        "email": "fiona.gallagher@company.com",
        "department": "Quality Assurance",
        "role": "QA & Test Automation Lead",
        "category": "tech",
        "skills": json.dumps(["Playwright", "PyTest", "Selenium", "Cypress", "API Testing", "Load Testing"]),
        "years_experience": 6,
        "availability_percent": 85,
        "performance_rating": 4.7,
        "current_projects": json.dumps([]),
        "bio": "Dedicated QA engineer driving end-to-end integration testing and automated regression suites."
    },
    {
        "name": "George Kumar",
        "email": "george.kumar@company.com",
        "department": "AI & Research",
        "role": "AI / ML Solutions Engineer",
        "category": "tech",
        "skills": json.dumps(["Python", "PyTorch", "LangChain", "LLMs", "RAG", "Vector DBs", "OpenAI API"]),
        "years_experience": 6,
        "availability_percent": 75,
        "performance_rating": 4.8,
        "current_projects": json.dumps(["Internal Knowledge Chatbot"]),
        "bio": "Machine learning and LLM integration specialist, building agentic and RAG workflows."
    },
    {
        "name": "Hannah Abbott",
        "email": "hannah.abbott@company.com",
        "department": "Security",
        "role": "Cybersecurity & InfoSec Engineer",
        "category": "tech",
        "skills": json.dumps(["AppSec", "OWASP", "Penetration Testing", "SOC2", "IAM", "Encryption"]),
        "years_experience": 8,
        "availability_percent": 70,
        "performance_rating": 4.8,
        "current_projects": json.dumps(["Annual SOC2 Audit"]),
        "bio": "Secures software lifecycles, conducts threat modeling, and enforces data compliance."
    },
    {
        "name": "Ian Malcolm",
        "email": "ian.malcolm@company.com",
        "department": "Data Platform",
        "role": "Principal Data Engineer",
        "category": "tech",
        "skills": json.dumps(["Apache Spark", "Kafka", "Snowflake", "dbt", "Airflow", "SQL", "Python"]),
        "years_experience": 11,
        "availability_percent": 100,
        "performance_rating": 4.9,
        "current_projects": json.dumps([]),
        "bio": "Big data pipelines, stream processing, and real-time analytical data marts."
    },
    {
        "name": "Julia Roberts",
        "email": "julia.roberts@company.com",
        "department": "IoT & Hardware",
        "role": "Embedded Systems Engineer",
        "category": "tech",
        "skills": json.dumps(["C++", "Rust", "FreeRTOS", "MQTT", "Hardware Protocols", "BLE"]),
        "years_experience": 7,
        "availability_percent": 90,
        "performance_rating": 4.7,
        "current_projects": json.dumps([]),
        "bio": "Low-power firmware and IoT telemetry pipeline architect."
    },
    {
        "name": "Kevin Bacon",
        "email": "kevin.bacon@company.com",
        "department": "Engineering",
        "role": "Junior Backend Developer",
        "category": "tech",
        "skills": json.dumps(["Python", "Django", "FastAPI", "SQLite", "Git", "REST APIs"]),
        "years_experience": 2,
        "availability_percent": 100,
        "performance_rating": 4.5,
        "current_projects": json.dumps([]),
        "bio": "Eager and fast learner capable of handling CRUD microservices, documentation, and unit tests."
    },
    {
        "name": "Laura Croft",
        "email": "laura.croft@company.com",
        "department": "Engineering",
        "role": "Frontend Developer (UI/WebGL)",
        "category": "tech",
        "skills": json.dumps(["Vue.js", "React", "Three.js", "CSS Animation", "WebGL", "TypeScript"]),
        "years_experience": 4,
        "availability_percent": 80,
        "performance_rating": 4.6,
        "current_projects": json.dumps([]),
        "bio": "Creates visually engaging data visualizations, interactive web components, and 3D web canvases."
    },
    {
        "name": "Mike Tyson",
        "email": "mike.tyson@company.com",
        "department": "Infrastructure & Cloud",
        "role": "Database Administrator & Optimization Specialist",
        "category": "tech",
        "skills": json.dumps(["PostgreSQL", "MySQL", "Redis", "Query Optimization", "Replication", "High Availability"]),
        "years_experience": 12,
        "availability_percent": 80,
        "performance_rating": 4.9,
        "current_projects": json.dumps([]),
        "bio": "Master of database indexing, partition schemes, backup strategies, and query tuning."
    },
    {
        "name": "Nina Simone",
        "email": "nina.simone@company.com",
        "department": "Engineering",
        "role": "Enterprise Solutions Architect",
        "category": "tech",
        "skills": json.dumps(["System Design", "Microservices", "Event-Driven Architecture", "Domain-Driven Design", "Java", "Python"]),
        "years_experience": 14,
        "availability_percent": 50,
        "performance_rating": 5.0,
        "current_projects": json.dumps(["Core Banking Redesign"]),
        "bio": "Translates complex business domains into scalable, fault-tolerant enterprise software topologies."
    },
    {
        "name": "Oscar Wilde",
        "email": "oscar.wilde@company.com",
        "department": "Infrastructure & Cloud",
        "role": "Site Reliability Engineer (SRE)",
        "category": "tech",
        "skills": json.dumps(["Datadog", "Prometheus", "Grafana", "Incident Response", "Chaos Engineering", "Linux"]),
        "years_experience": 6,
        "availability_percent": 100,
        "performance_rating": 4.7,
        "current_projects": json.dumps([]),
        "bio": "Observability champion, automated monitoring, alerting, and SLA enforcement."
    },

    # ----------------- NON-TECHNICAL EMPLOYEES (15) -----------------
    {
        "name": "Sarah Connor",
        "email": "sarah.connor@company.com",
        "department": "Project Management",
        "role": "Senior Technical Project Manager",
        "category": "hybrid",
        "skills": json.dumps(["Agile", "Scrum", "Risk Management", "Jira", "Sprint Planning", "Stakeholder Communication"]),
        "years_experience": 9,
        "availability_percent": 75,
        "performance_rating": 4.9,
        "current_projects": json.dumps(["Q4 Infrastructure Initiative"]),
        "bio": "Flawless sprint execution, budget containment, and cross-functional dependency management."
    },
    {
        "name": "Marcus Aurelius",
        "email": "marcus.aurelius@company.com",
        "department": "Product Management",
        "role": "Principal Product Manager",
        "category": "non_tech",
        "skills": json.dumps(["Product Roadmap", "User Stories", "PRDs", "Market Research", "Feature Prioritization", "A/B Testing"]),
        "years_experience": 11,
        "availability_percent": 60,
        "performance_rating": 4.9,
        "current_projects": json.dumps(["B2B Expansion"]),
        "bio": "Strategic product leader driving market fit, user value propositions, and metrics-driven delivery."
    },
    {
        "name": "Emma Watson",
        "email": "emma.watson@company.com",
        "department": "Design",
        "role": "Senior UI/UX Product Designer",
        "category": "hybrid",
        "skills": json.dumps(["Figma", "User Research", "Wireframing", "Design Systems", "Prototyping", "Usability Testing"]),
        "years_experience": 7,
        "availability_percent": 85,
        "performance_rating": 4.8,
        "current_projects": json.dumps([]),
        "bio": "Blends aesthetics with accessibility, crafting delightful and intuitive digital experiences."
    },
    {
        "name": "Liam Neeson",
        "email": "liam.neeson@company.com",
        "department": "Design & Brand",
        "role": "Creative Director & Brand Strategist",
        "category": "non_tech",
        "skills": json.dumps(["Brand Identity", "Visual Direction", "Typography", "Campaign Creative", "Brand Guidelines"]),
        "years_experience": 13,
        "availability_percent": 70,
        "performance_rating": 4.9,
        "current_projects": json.dumps([]),
        "bio": "Guiding corporate identity, messaging consistency, and creative storytelling across global channels."
    },
    {
        "name": "Olivia Wilde",
        "email": "olivia.wilde@company.com",
        "department": "Content & Editorial",
        "role": "Senior Content Strategist & Copywriter",
        "category": "non_tech",
        "skills": json.dumps(["Copywriting", "SEO Content", "Press Releases", "Technical Writing", "Brand Voice", "Whitepapers"]),
        "years_experience": 6,
        "availability_percent": 95,
        "performance_rating": 4.7,
        "current_projects": json.dumps([]),
        "bio": "High-impact storytelling for products, corporate newsletters, landing pages, and executive thought leadership."
    },
    {
        "name": "Noah Centineo",
        "email": "noah.centineo@company.com",
        "department": "Marketing",
        "role": "Growth Marketing Lead",
        "category": "non_tech",
        "skills": json.dumps(["Digital Marketing", "Paid Ads", "Google Ads", "Social Campaigns", "Funnel Optimization", "HubSpot"]),
        "years_experience": 5,
        "availability_percent": 100,
        "performance_rating": 4.6,
        "current_projects": json.dumps([]),
        "bio": "Data-backed digital acquisition, lead generation funnels, and multichannel conversion growth."
    },
    {
        "name": "Chloe Grace",
        "email": "chloe.grace@company.com",
        "department": "Corporate Events & Operations",
        "role": "Corporate Events & Logistics Coordinator",
        "category": "non_tech",
        "skills": json.dumps(["Event Planning", "Venue Management", "Vendor Negotiation", "Catering Coordination", "Budget Management", "Onsite Logistics"]),
        "years_experience": 8,
        "availability_percent": 100,
        "performance_rating": 4.9,
        "current_projects": json.dumps([]),
        "bio": "Expert in producing large scale company galas, international conferences, and internal summits."
    },
    {
        "name": "Daniel Craig",
        "email": "daniel.craig@company.com",
        "department": "Public Relations",
        "role": "PR & Corporate Communications Lead",
        "category": "non_tech",
        "skills": json.dumps(["Public Relations", "Crisis Management", "Media Outreach", "Spokesperson Prep", "Press Conferences"]),
        "years_experience": 10,
        "availability_percent": 80,
        "performance_rating": 4.8,
        "current_projects": json.dumps([]),
        "bio": "Manages press contacts, protects corporate reputation, and orchestrates major product launch announcements."
    },
    {
        "name": "Rachel Green",
        "email": "rachel.green@company.com",
        "department": "Human Resources",
        "role": "People Operations & HR Specialist",
        "category": "non_tech",
        "skills": json.dumps(["Employee Relations", "Onboarding", "Talent Acquisition", "Conflict Resolution", "Performance Reviews", "Company Culture"]),
        "years_experience": 7,
        "availability_percent": 80,
        "performance_rating": 4.7,
        "current_projects": json.dumps([]),
        "bio": "Champion for office culture, change management, employee wellness, and organizational development."
    },
    {
        "name": "Harvey Specter",
        "email": "harvey.specter@company.com",
        "department": "Legal & Compliance",
        "role": "Corporate Counsel & Contracts Specialist",
        "category": "non_tech",
        "skills": json.dumps(["Contract Negotiation", "Vendor Agreements", "IP Protection", "GDPR", "Corporate Compliance", "Risk Assessment"]),
        "years_experience": 12,
        "availability_percent": 50,
        "performance_rating": 5.0,
        "current_projects": json.dumps(["Enterprise Master Service Agreements"]),
        "bio": "Vigorous contract vetting, risk mitigation, and regulatory compliance advisory."
    },
    {
        "name": "Monica Geller",
        "email": "monica.geller@company.com",
        "department": "Operations",
        "role": "Facilities & Office Operations Manager",
        "category": "non_tech",
        "skills": json.dumps(["Office Operations", "Vendor Management", "Space Planning", "Procurement", "Safety Protocols", "Budget Tracking"]),
        "years_experience": 8,
        "availability_percent": 100,
        "performance_rating": 4.9,
        "current_projects": json.dumps([]),
        "bio": "Hyper-organized operational powerhouse managing workspaces, physical transitions, and resource distribution."
    },
    {
        "name": "Chandler Bing",
        "email": "chandler.bing@company.com",
        "department": "Finance",
        "role": "Senior Financial & Budget Analyst",
        "category": "non_tech",
        "skills": json.dumps(["Financial Modeling", "Budget Tracking", "Cost-Benefit Analysis", "Variance Analysis", "Excel/Sheets", "Forecasting"]),
        "years_experience": 9,
        "availability_percent": 85,
        "performance_rating": 4.8,
        "current_projects": json.dumps([]),
        "bio": "Rigorous financial oversight, cost projections, and corporate resource allocation analysis."
    },
    {
        "name": "Phoebe Buffay",
        "email": "phoebe.buffay@company.com",
        "department": "Marketing & Community",
        "role": "Community Engagement & Social Media Lead",
        "category": "non_tech",
        "skills": json.dumps(["Community Building", "Social Media", "Customer Engagement", "Influencer Relations", "Content Creation"]),
        "years_experience": 5,
        "availability_percent": 90,
        "performance_rating": 4.6,
        "current_projects": json.dumps([]),
        "bio": "Builds authentic engagement across social channels, customer forums, and brand advocate circles."
    },
    {
        "name": "Ross Geller",
        "email": "ross.geller@company.com",
        "department": "Research & Strategy",
        "role": "Market Research & Knowledge Curator",
        "category": "non_tech",
        "skills": json.dumps(["Competitive Analysis", "Market Research", "Survey Design", "Documentation", "Whitepapers"]),
        "years_experience": 8,
        "availability_percent": 80,
        "performance_rating": 4.6,
        "current_projects": json.dumps([]),
        "bio": "Conducts deep market investigations, synthesizes competitor landscapes, and delivers rigorous reports."
    },
    {
        "name": "Joey Tribbiani",
        "email": "joey.tribbiani@company.com",
        "department": "Client Relations & Sales",
        "role": "Client Partnerships & Account Executive",
        "category": "non_tech",
        "skills": json.dumps(["Client Pitching", "Relationship Management", "Customer Success", "Presentations", "Account Growth"]),
        "years_experience": 6,
        "availability_percent": 75,
        "performance_rating": 4.7,
        "current_projects": json.dumps([]),
        "bio": "Charismatic communicator dedicated to securing stakeholder buy-in, relationship retention, and client trust."
    }
]

def init_database():
    """Initializes schema and populates sample employees if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    if count == 0:
        for emp in SAMPLE_EMPLOYEES:
            cursor.execute("""
                INSERT INTO employees (
                    name, email, department, role, category, skills, 
                    years_experience, availability_percent, performance_rating, 
                    current_projects, bio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emp["name"], emp["email"], emp["department"], emp["role"], emp["category"],
                emp["skills"], emp["years_experience"], emp["availability_percent"],
                emp["performance_rating"], emp["current_projects"], emp["bio"]
            ))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized with sample employees.")

