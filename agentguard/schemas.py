from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Policy(BaseModel):
    id: str
    version: str
    status: Literal["draft", "approved", "deprecated"] = "draft"
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    owners: List[str] = Field(default_factory=list)
    title: str
    text: str
    tags: List[str] = Field(default_factory=list)

class ValidateRequest(BaseModel):
    action_type: Literal["refund","account_update","response"]
    proposed_action: str = Field(min_length=1, max_length=8000)
    amount: float = Field(default=0, ge=0)
    order_status: Literal["delivered","cancelled","processing","unknown"] = "unknown"
    eligibility: Literal["yes","no","unknown"] = "unknown"
    authorized: Literal["yes","no","unknown"] = "unknown"

class Evidence(BaseModel):
    policy_id: str
    title: str
    text: str
    score: float = 0

class Check(BaseModel):
    name: str
    result: Literal["PASS","FAIL","REVIEW"]
    details: str

class ValidateResponse(BaseModel):
    decision: Literal["ALLOW","BLOCK","ESCALATE"]
    reason: str
    checks: list[Check]
    evidence: list[Evidence]
    retrieval_ms: float
    validation_ms: float
    total_ms: float
    retrieval_backend: str

