# ⚡ GridGuard AI
Multi-agent incident response for Pakistan electricity outages and billing disputes, now powered by Ai.

## Architecture
Orchestrator → Location, Bill Auditor, Outage Detector, Weather, Regulation, Grid Analyst → Evidence → Action → Human Approval.

* `agent_modules/` : deterministic specialist agents (source of truth for numbers). `agents.py` is a compatibility facade.
* `agent_modules/crew_runner.py` : **CrewAI layer**. Each specialist is a real `crewai.Agent` with its own tool, tasks run in a sequential `crewai.Crew`, and a *Case Officer* agent writes the briefing. Falls back to the rules engine if CrewAI, the API key or the LLM is unavailable.
* `ui_theme.py` / `ui_components.py` : 5 premium themes (Midnight Neon, Aurora Emerald, Royal Gold, Crimson Grid, Ocean Glass), KPI cards, pipeline stepper, gauge and bar charts.
* `app.py` : tabs 🚀 Investigate · 🕵️ Agent Trace · 📊 Analytics · 📝 Complaint & Approval · 🧠 Crew Briefing · ℹ️ About.

## Run
    pip install -r requirements.txt     # Python 3.10 - 3.13 (CrewAI requirement)
    streamlit run app.py
    pytest

## Using CrewAI
Pick **🤖 CrewAI crew (LLM)** in the sidebar, choose a provider (Gemini, Groq, OpenAI, Anthropic) and paste its key,
or set it as an env var / Streamlit secret: `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`.
Optional model override uses LiteLLM names, e.g. `groq/llama-3.3-70b-versatile`.

## Deploy
Push to GitHub → share.streamlit.io → main file `app.py`. Add your API key under *Secrets*. Use a Python 3.11/3.12 runtime.

## Notes
Tariff slabs (`bill_auditor.py`) and scheduled-outage allowances (`outage_detector.py`) are ILLUSTRATIVE; update from NEPRA/DISCO notifications. Nothing is filed without human approval.
