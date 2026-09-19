import time
def validate(req, evidence):
    start=time.perf_counter(); checks=[]; reasons=[]; decision="ALLOW"
    def add(n,r,d): checks.append({"name":n,"result":r,"details":d})
    if not evidence: decision="ESCALATE"; reasons.append("No relevant policy evidence retrieved.")
    if req.authorized=="no": decision="BLOCK"; reasons.append("Agent authorization denied."); add("Authorization","FAIL","Explicitly denied.")
    elif req.authorized=="unknown":
        if decision!="BLOCK": decision="ESCALATE"
        reasons.append("Agent authorization is unverified."); add("Authorization","REVIEW","Unknown.")
    else: add("Authorization","PASS","Confirmed.")
    if req.action_type=="refund":
        if req.amount<=0: decision="BLOCK"; reasons.append("Refund amount must be positive."); add("Positive amount","FAIL","Must exceed zero.")
        else: add("Positive amount","PASS",f"Amount {req.amount:.2f}.")
        if req.order_status in ("processing","unknown"):
            if decision!="BLOCK": decision="ESCALATE"
            reasons.append("Order status is insufficient."); add("Order status","REVIEW",req.order_status)
        else: add("Order status","PASS",req.order_status)
        if req.eligibility=="no": decision="BLOCK"; reasons.append("Eligibility failed."); add("Eligibility","FAIL","Marked ineligible.")
        elif req.eligibility=="unknown":
            if decision!="BLOCK": decision="ESCALATE"
            reasons.append("Eligibility unverified."); add("Eligibility","REVIEW","Needs verification.")
        else: add("Eligibility","PASS","Confirmed.")
        # Example policy only. Configure using approved policy before production.
        if req.amount>5000: decision="ESCALATE" if decision!="BLOCK" else decision; reasons.append("Amount exceeds sample auto-processing threshold."); add("Sample threshold","REVIEW","Above ₹5,000; human approval required.")
        else: add("Sample threshold","PASS","Within sample threshold.")
    else:
        if decision=="ALLOW": decision="ESCALATE"
        reasons.append("No action-specific rule is configured."); add("Action-specific rule","REVIEW","Not configured.")
    return decision,(" ".join(reasons) if reasons else "All configured checks passed."),checks,(time.perf_counter()-start)*1000
