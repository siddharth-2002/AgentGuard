import os, requests, streamlit as st
import subprocess

st.set_page_config(page_title="AgentGuard",page_icon="🛡️",layout="wide")
st.title("🛡️ AgentGuard")
st.caption("Policy retrieval + deterministic runtime validation")

api=st.sidebar.text_input("API base URL",os.getenv("AGENTGUARD_API_URL","http://localhost:8000"))
key=st.sidebar.text_input("API key",os.getenv("AGENTGUARD_API_KEY","change-me-in-production"),type="password")
st.sidebar.info("Demo environment. No external action is executed. Sample policies/thresholds are illustrative.")

# Create tabs for the demo
tab_val, tab_audit, tab_arch, tab_bench = st.tabs(["🛡️ Validator", "📋 Audit Trail", "📐 Architecture", "📊 Benchmark"])

with tab_val:
    with st.form("validate"):
        kind=st.selectbox("Action type",["refund","account_update","response"])
        action=st.text_area("Proposed agent action","Issue a ₹2,000 refund for order #1234.")
        amount=st.number_input("Amount (₹)",min_value=0.0,value=2000.0) if kind=="refund" else 0.0
        status=st.selectbox("Order status",["delivered","cancelled","processing","unknown"])
        eligibility=st.selectbox("Eligibility",["yes","no","unknown"],index=2)
        authorized=st.selectbox("Agent authorized?",["yes","no","unknown"],index=0)
        submit=st.form_submit_button("Validate",type="primary")
    
    if submit:
        payload={"action_type":kind,"proposed_action":action,"amount":amount,"order_status":status,"eligibility":eligibility,"authorized":authorized}
        try:
            r=requests.post(api.rstrip("/")+"/v1/validate",json=payload,headers={"X-API-Key":key},timeout=30)
            if r.ok:
                d=r.json(); st.write(d["reason"])
                (st.success if d["decision"]=="ALLOW" else st.error if d["decision"]=="BLOCK" else st.warning)(d["decision"])
                a,b,c=st.columns(3); a.metric("Retrieval",f'{d["retrieval_ms"]:.2f} ms'); b.metric("Validation",f'{d["validation_ms"]:.2f} ms'); c.metric("Total",f'{d["total_ms"]:.2f} ms')
                st.subheader("Checks"); st.dataframe(d["checks"],use_container_width=True,hide_index=True)
                st.subheader("Evidence")
                for e in d["evidence"]:
                    with st.expander(f'{e["policy_id"]}: {e["title"]}'): st.write(e["text"])
            else: st.error(f"API error {r.status_code}: {r.text}")
        except requests.RequestException as e: st.error(f"Cannot reach API: {e}")

with tab_audit:
    st.write("Immutable ledger of all runtime decisions.")
    if st.button("Refresh audit log"):
        try:
            r=requests.get(api.rstrip("/")+"/v1/audit",headers={"X-API-Key":key},timeout=10); r.raise_for_status()
            st.dataframe(r.json()["events"],use_container_width=True,hide_index=True)
        except requests.RequestException as e: st.error(str(e))

with tab_arch:
    st.write("### System Architecture")
    st.write("AgentGuard sits securely between the AI Agent and the Target Tool, ensuring that semantic retrieval is decoupled from deterministic validation.")
    
    # Read the ARCHITECTURE.md file
    try:
        with open("ARCHITECTURE.md", "r") as f:
            arch_content = f.read()
            # Streamlit doesn't render Mermaid natively out of the box in all versions, 
            # but we can display the markdown which extensions/users can read.
            st.markdown(arch_content)
    except FileNotFoundError:
        st.error("ARCHITECTURE.md not found.")

with tab_bench:
    st.write("### Retrieval Benchmark")
    st.write("Run the benchmark script against the fixed query set to evaluate latency and accuracy.")
    
    if st.button("Run Benchmark"):
        try:
            # We will just run the script and capture the output
            result = subprocess.run(["python", "benchmark.py"], capture_output=True, text=True, check=True)
            st.code(result.stdout, language="text")
        except Exception as e:
            st.error(f"Failed to run benchmark: {e}")
