import time, uuid, hmac
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
from .config import settings
from .schemas import ValidateRequest, ValidateResponse
from .policy import load_policies
from .retrieval import retrieve
from .validator import validate
from .db import init_db, write_audit, recent_audit
app=FastAPI(title="AgentGuard API",version="1.0.0",description="Policy retrieval and runtime action validation")
@app.on_event("startup")
def startup(): init_db()
def authenticate(x_api_key):
    if settings.environment=="production" and settings.api_key=="change-me-in-production":
        raise HTTPException(500,"Set a strong AGENTGUARD_API_KEY before production.")
    if not x_api_key or not hmac.compare_digest(x_api_key,settings.api_key):
        raise HTTPException(401,"Invalid API key")
@app.get("/health")
def health(): return {"status":"ok","environment":settings.environment}
@app.post("/v1/validate",response_model=ValidateResponse)
def validate_endpoint(req:ValidateRequest,x_api_key:str=Header(default="")):
    authenticate(x_api_key)
    if len(req.proposed_action)>settings.max_request_chars: raise HTTPException(413,"Request too large")
    start=time.perf_counter()
    try: evidence,ret_ms,backend=retrieve(f"{req.action_type} {req.proposed_action} amount {req.amount} status {req.order_status} eligibility {req.eligibility}",load_policies(),settings)
    except Exception as e: raise HTTPException(502,f"Retrieval backend error: {type(e).__name__}") from e
    decision,reason,checks,val_ms=validate(req,evidence); total=(time.perf_counter()-start)*1000
    now=datetime.now(timezone.utc).isoformat(); event={"id":str(uuid.uuid4()),"created_at":now,"action_type":req.action_type,"decision":decision,"retrieval_ms":ret_ms,"total_ms":total,"backend":backend,"payload":req.model_dump()}
    write_audit(event)
    return {"decision":decision,"reason":reason,"checks":checks,"evidence":[{"policy_id":str(p.get("id","unknown")),"title":p.get("title","Policy"),"text":p.get("text",""),"score":p.get("score",0)} for p in evidence],"retrieval_ms":ret_ms,"validation_ms":val_ms,"total_ms":total,"retrieval_backend":backend}
@app.get("/v1/audit")
def audit(limit:int=50,x_api_key:str=Header(default="")):
    authenticate(x_api_key)
    if not 1<=limit<=200: raise HTTPException(400,"limit must be 1..200")
    return {"events":recent_audit(limit)}
