from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class MessageType(str, Enum):
    PROJECT_ANALYSIS_REQUEST = "PROJECT_ANALYSIS_REQUEST"
    A2A_CANDIDATE_QUERY = "A2A_CANDIDATE_QUERY"
    A2A_CANDIDATE_RESPONSE = "A2A_CANDIDATE_RESPONSE"
    A2A_CONFLICT_QUERY = "A2A_CONFLICT_QUERY"
    A2A_CONFLICT_RESPONSE = "A2A_CONFLICT_RESPONSE"
    FINAL_ROSTER_DECISION = "FINAL_ROSTER_DECISION"

class RoleRequirement(BaseModel):
    role_name: str = Field(..., description="E.g., Senior Backend Engineer, UI/UX Designer, PR Lead")
    category: str = Field(..., description="'tech', 'non_tech', or 'hybrid'")
    keywords: List[str] = Field(default_factory=list, description="Key skills or concepts needed")
    min_experience_years: int = Field(default=2, description="Minimum years of experience")
    required_bandwidth_percent: int = Field(default=40, description="Minimum availability needed")
    is_leadership: bool = Field(default=False, description="Whether this is a lead/architect/manager role")

class CandidateMatch(BaseModel):
    id: int
    name: str
    email: str
    department: str
    role: str
    category: str
    skills: List[str]
    years_experience: int
    availability_percent: int
    performance_rating: float
    match_score: float
    current_projects: List[str]
    bio: Optional[str] = None

class A2AMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sender: str
    recipient: str
    message_type: MessageType
    summary: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = Field(None, description="The internal reasoning/agent thought behind this message")

