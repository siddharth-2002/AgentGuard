from types import SimpleNamespace
from agentguard.validator import validate
def req(**kw):
    d=dict(action_type="refund",amount=1000,order_status="delivered",eligibility="yes",authorized="yes")
    d.update(kw); return SimpleNamespace(**d)
def test_unknown_eligibility_escalates():
    assert validate(req(eligibility="unknown"),[{"text":"policy"}])[0]=="ESCALATE"
def test_unauthorized_blocks():
    assert validate(req(authorized="no"),[{"text":"policy"}])[0]=="BLOCK"
def test_no_evidence_escalates():
    assert validate(req(),[])[0]=="ESCALATE"
def test_over_threshold_escalates():
    assert validate(req(amount=6000),[{"text":"policy"}])[0]=="ESCALATE"
