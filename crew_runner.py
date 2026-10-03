"""CrewAI integration for GridGuard AI.

Design
------
The eight deterministic specialist agents (rules, tariff maths, weather, ...) stay the
source of truth for numbers and findings. CrewAI wraps them:

* every specialist becomes a real ``crewai.Agent`` (role / goal / backstory / Groq LLM)
* each one owns a ``crewai.tools`` tool that executes its deterministic logic
* ``crewai.Task`` objects run in a sequential ``crewai.Crew``
* a ninth CrewAI agent, the *Case Officer*, writes the final briefing

If CrewAI is not installed, no API key is set, or the LLM call fails, ``run_crew_case``
falls back to the pure rules pipeline, so the app never breaks. Human approval is
still required before anything is filed.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict

from .base import Finding
from .orchestrator import PIPELINE

# ---- LLM: Groq only (LiteLLM model string used by CrewAI) -----------------------------
GROQ_MODEL = "groq/llama-3.3-70b-versatile"
GROQ_ENV = "GROQ_API_KEY"

# Role / goal / backstory for each specialist, keyed by the deterministic agent name.
PERSONAS = {
    "Location Agent": ("DISCO Locator", "Identify the electricity distribution company serving the consumer.",
                       "A former NEPRA field mapper who knows every DISCO territory in Pakistan."),
    "Bill Auditor": ("Tariff & Bill Auditor", "Recompute the bill against the tariff slabs and flag anomalies.",
                     "A forensic accountant who has audited thousands of inflated electricity bills."),
    "Outage Detector": ("Outage Analyst", "Measure the outage and the excess over the scheduled allowance.",
                        "A load-management engineer who reads Roman Urdu complaints like a native."),
    "Weather / Environment Agent": ("Weather & Environment Scout", "Check heat and wind conditions that stress the grid.",
                                    "A meteorologist focused on South Asian heatwaves and storms."),
    "Regulation Agent": ("Regulatory Guide", "Prepare the escalation ladder and evidence checklist.",
                         "A consumer-rights lawyer who knows NEPRA, the Ombudsman and the Citizen Portal."),
    "Grid Analyst": ("Grid Cause Analyst", "Rank the most likely technical causes of the outage.",
                     "A transmission engineer who diagnoses feeder and transformer faults."),
    "Investigation / Evidence Agent": ("Evidence Investigator", "Score the strength of the case from all findings.",
                                       "A senior investigator who only trusts evidence that survives cross-examination."),
    "Action Agent": ("Complaint Drafter", "Draft a formal complaint for human review. Never file anything.",
                     "A bilingual (English / Roman Urdu) complaint writer."),
}

OFFICER = ("Case Officer", "Write a short, plain-language briefing for the consumer.",
           "A calm senior caseworker who explains technical findings simply and always reminds "
           "the consumer that nothing is filed without their approval.")


def crewai_available() -> bool:
    try:
        import crewai  # noqa: F401
        return True
    except Exception:
        return False


class CrewSession:
    """Shared state for one case. Runs deterministic agents on demand, in pipeline order."""

    def __init__(self, case: dict, on_step=None):
        self.case, self.on_step = case, on_step
        self.findings, self.trace = [], []
        self.ctx = {"findings": self.findings}
        self.agents = [a() for a in PIPELINE]
        self.done = set()

    def run_step(self, name: str) -> Finding:
        """Run agent ``name`` (and any earlier agents it depends on) exactly once."""
        names = [a.name for a in self.agents]
        if name not in names:
            raise KeyError(name)
        for ag in self.agents[: names.index(name) + 1]:
            if ag.name in self.done:
                continue
            t0 = time.time()
            try:
                f = ag.run(self.case, self.ctx)
            except Exception as e:  # one failing agent must not kill the case
                f = Finding(ag.name, f"Agent error: {e}", "warn", 0.0)
            self.done.add(ag.name)
            self.findings.append(f)
            if ag.name.startswith("Investigation"):
                self.ctx["evidence"] = f.data.get("bullets", [])
            self.trace.append({"agent": ag.name, "ms": int((time.time() - t0) * 1000), "finding": f})
            if self.on_step:
                self.on_step(self.trace[-1])
        return next(t["finding"] for t in self.trace if t["agent"] == name)

    def finish(self) -> None:
        """Make sure every agent ran even if the LLM skipped a tool call."""
        for ag in self.agents:
            self.run_step(ag.name)

    def result(self, **extra) -> dict:
        return {"ctx": self.ctx, "trace": self.trace, "status": "PENDING_APPROVAL", **extra}


def _finding_json(f: Finding) -> str:
    return json.dumps(asdict(f), default=str)[:3500]


def _make_tools(session: CrewSession):
    """Build one CrewAI tool per deterministic agent, bound to the session."""
    from crewai.tools import tool

    tools = {}
    for ag in session.agents:
        persona = PERSONAS[ag.name][0]

        def _fn(query: str = "run", _name=ag.name) -> str:
            return _finding_json(session.run_step(_name))

        _fn.__name__ = "run_" + "".join(c if c.isalnum() else "_" for c in persona.lower())
        _fn.__doc__ = (f"Run the {persona} analysis for the current case and return its finding as JSON "
                       f"(summary, severity, confidence, data). The argument is only a short reason.")
        tools[ag.name] = tool(persona)(_fn)
    return tools


def build_crew(session: CrewSession, llm):
    """Create the CrewAI Crew: 8 specialists + the Case Officer, run sequentially."""
    from crewai import Agent as CAgent, Crew, Process, Task

    tools = _make_tools(session)
    case_txt = json.dumps({k: v for k, v in session.case.items() if v not in (None, "")}, default=str)
    agents, tasks = [], []
    for ag in session.agents:
        role, goal, story = PERSONAS[ag.name]
        a = CAgent(role=role, goal=goal, backstory=story, tools=[tools[ag.name]], llm=llm,
                   allow_delegation=False, verbose=False, max_iter=3)
        t = Task(description=(f"Case: {case_txt}\nUse your tool exactly once, then reply with ONE sentence "
                              f"describing the result in plain English."),
                 expected_output="One plain-English sentence summarising the tool result.",
                 agent=a, context=list(tasks[-2:]) or None)
        agents.append(a)
        tasks.append(t)
    role, goal, story = OFFICER
    officer = CAgent(role=role, goal=goal, backstory=story, llm=llm, allow_delegation=False, verbose=False)
    tasks.append(Task(
        description=("Using the previous results, write a briefing of at most 120 words for the consumer: "
                     "what happened, how strong the case is, and the next step. End with: "
                     "'Nothing is filed until you approve.'"),
        expected_output="A briefing of at most 120 words.", agent=officer, context=list(tasks)))
    agents.append(officer)
    return Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)


def run_crew_case(case: dict, api_key: str | None = None, model: str | None = None, on_step=None) -> dict:
    """Investigate with a CrewAI crew powered by Groq; fall back to the rules pipeline on any problem.

    The returned dict matches ``Orchestrator.investigate`` plus ``mode``, ``crew_report``
    and ``warning`` keys.
    """
    os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    session = CrewSession(case, on_step)
    key = api_key or os.getenv(GROQ_ENV)

    def fallback(why: str) -> dict:
        session.finish()
        return session.result(mode="rules", crew_report="", warning=why)

    if not crewai_available():
        return fallback("CrewAI is not installed (pip install crewai). Ran the rules engine instead.")
    if not key:
        return fallback("No GROQ_API_KEY provided. Ran the rules engine instead.")
    try:
        from crewai import LLM
        llm = LLM(model=model or GROQ_MODEL, api_key=key, temperature=0.2)
        crew = build_crew(session, llm)
        out = crew.kickoff()
        session.finish()  # guarantee all 8 agents ran, whatever the LLM did
        report = str(getattr(out, "raw", out)).strip()
        return session.result(mode="crewai", crew_report=report, warning="")
    except Exception as e:  # network / quota / schema errors must not lose the case
        return fallback(f"CrewAI run failed ({type(e).__name__}: {str(e)[:160]}). Ran the rules engine instead.")
