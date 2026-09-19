# AgentGuard — production-oriented starter

This is a runnable development scaffold, **not a certified or production-ready security product**. It includes a FastAPI service, Streamlit UI, local policy corpus, deterministic validation, API-key gate, SQLite audit trail, tests, and Docker Compose.

## Project Structure
```text
AgentGuard/
├── agentguard/             # Core backend logic (FastAPI)
│   ├── main.py             # FastAPI routes & entrypoint
│   ├── policy.py           # Policy corpus loader & schema filter
│   ├── retrieval.py        # Provider interfaces (Moss/Local)
│   ├── schemas.py          # Strict Pydantic models for I/O
│   └── validator.py        # Deterministic rule engine
├── data/
│   └── policies.json       # JSON database of approved policies
├── tests/                  # Unit and integration tests
├── app.py                  # Streamlit UI dashboard
├── benchmark.py            # Latency & accuracy evaluation script
└── ARCHITECTURE.md         # Mermaid architecture diagram
```

## Windows quick start
Install Python 3.11, extract ZIP, double-click `run_windows.bat`. The script installs dependencies, starts API and UI. Open Streamlit's displayed URL.

## Manual start
Terminal 1:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn agentguard.main:app --reload
```

Terminal 2:
```bash
.venv\Scripts\activate
streamlit run app.py
```
API docs: http://localhost:8000/docs

## Tests
`pytest -q`

## Moss setup
The Moss connector is deliberately an adapter stub because the exact current Moss API/SDK contract must be taken from official Moss documentation/account. Set `MOSS_PROJECT_ID` and `MOSS_PROJECT_KEY` in environment, then adapt `agentguard/retrieval.py` to the actual authentication, request schema, response schema, and SDK. Never represent local baseline metrics as Moss measurements.

## Before production
- Replace demo policies and sample ₹5,000 threshold with approved, versioned policy rules.
- Replace shared API key with enterprise identity/OIDC, scoped authorization, rotation, and secrets management.
- Use managed PostgreSQL or equivalent, migrations, encryption, retention controls, backups, and access-controlled audit logs.
- Add tenant isolation, rate limiting, request IDs, structured logs, metrics, tracing, alerting, CI/CD, dependency scanning, SAST/DAST, and load tests.
- Validate all tool actions independently at the execution boundary; never treat retrieval or this demo decision as authorization.
- Add human approval and idempotency for consequential operations.
- Review privacy, threat model, prompt-injection handling, incident response, and legal/compliance requirements.
- Test Moss relevance and p50/p95 latency with a fixed benchmark corpus.
