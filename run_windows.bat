@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    py -m venv .venv
)
call .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
start "AgentGuard API" cmd /k "uvicorn agentguard.main:app --host 127.0.0.1 --port 8000"
timeout /t 3 >nul
streamlit run app.py
