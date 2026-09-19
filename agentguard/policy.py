import json
from datetime import datetime, timezone
from pathlib import Path
from .schemas import Policy

POLICY_PATH = Path(__file__).resolve().parent.parent / "data" / "policies.json"

def load_policies() -> list[Policy]:
    data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Policy corpus must be a JSON list")
    
    policies = []
    now = datetime.now(timezone.utc)
    for p in data:
        policy = Policy(**p)
        
        if policy.status != "approved":
            continue
            
        if policy.effective_date and policy.effective_date > now:
            continue
            
        if policy.expiration_date and policy.expiration_date < now:
            continue
            
        policies.append(policy)
        
    return policies

