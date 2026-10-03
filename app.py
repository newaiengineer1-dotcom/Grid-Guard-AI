import os

import streamlit as st

import ui_components as ui
from agents import Orchestrator, PROVIDERS, crewai_available, run_crew_case
from ui_theme import THEME, css

st.set_page_config(page_title="GridGuard AI", page_icon="⚡", layout="wide")

CITIES = ["Lahore", "Karachi", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Gujranwala", "Peshawar",
          "Quetta", "Hyderabad", "Sukkur"]
RULES, CREW = "⚙️ Rules engine (offline)", "🤖 CrewAI crew (LLM)"


def secret(name: str) -> str:
    try:
        return st.secrets.get(name, "") or os.getenv(name, "")
    except Exception:
        return os.getenv(name, "")


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 🧠 Engine")
    engine = st.radio("Engine", [RULES, CREW], label_visibility="collapsed",
                      help="CrewAI runs each specialist as a real CrewAI agent with an LLM.")
    provider, api_key, model = "Google Gemini", "", ""
    if engine == CREW:
        if not crewai_available():
            st.warning("CrewAI is not installed here. `pip install crewai` (Python 3.10-3.13).")
        provider = st.selectbox("🔌 LLM provider", list(PROVIDERS))
        env = PROVIDERS[provider]["env"]
        api_key = st.text_input(f"🔑 {env}", value=secret(env), type="password")
        model = st.text_input("🧩 Model override (optional)", placeholder=PROVIDERS[provider]["model"])

    st.markdown("## 📋 Case input")
    city = st.selectbox("🏙️ City", CITIES)
    area = st.selectbox("🏘️ Area type", ["urban", "mixed", "rural"])
    name, cno = st.text_input("👤 Your name"), st.text_input("🔢 Consumer no.")
    units = st.number_input("⚡ Units this month", 0)
    billed = st.number_input("💰 Billed amount (Rs)", 0)
    prev = st.number_input("📆 Units last month", 0)
    hours = st.number_input("🕒 Outage hours today", 0.0, 24.0, 0.0)
    temp = st.number_input("🌡️ Temperature °C (used if offline)", 0, 55, 35)
    st.file_uploader("📸 Bill photo (attached as evidence)", type=["png", "jpg", "jpeg", "pdf"])

st.markdown(css(THEME), unsafe_allow_html=True)
st.markdown(ui.hero("CrewAI multi-agent crew" if engine == CREW else "Rules-based agents", crewai_available()),
            unsafe_allow_html=True)

tab_go, tab_trace, tab_stats, tab_act, tab_brief, tab_about = st.tabs(
    ["🚀 Investigate", "🕵️ Agent Trace", "📊 Analytics", "📝 Complaint & Approval", "🧠 Crew Briefing", "ℹ️ About"])

# ---------------------------------------------------------------- investigate
with tab_go:
    text = st.text_area("🗣️ Describe the problem (Urdu / Roman Urdu / English)",
                        "Bijli 4 ghantay se ja rahi hai aur bill bhi bohat zyada aya hai.", height=110)
    launch = st.button("🚨 Launch investigation", type="primary")
    pipe = st.empty()
    pipe.markdown(ui.stepper(set()), unsafe_allow_html=True)

    if launch:
        case = dict(text=text, city=city, area_type=area, name=name, consumer_no=cno, units=units,
                    billed=billed, prev_units=prev, outage_hours=hours, temp_c=temp)
        done = set()

        def on_step(t):
            done.add(t["agent"])
            pipe.markdown(ui.stepper(done), unsafe_allow_html=True)

        label = "Crew is investigating..." if engine == CREW else "Agents investigating..."
        with st.spinner(label):
            if engine == CREW:
                result = run_crew_case(case, provider, api_key or None, model or None, on_step)
            else:
                result = Orchestrator().investigate(case, on_step)
                result.update(mode="rules", crew_report="", warning="")
        st.session_state.update(result=result, case=case)
        st.toast("Investigation complete", icon="✅")

    res, case = st.session_state.get("result"), st.session_state.get("case")
    if res:
        pipe.markdown(ui.stepper({t["agent"] for t in res["trace"]}), unsafe_allow_html=True)
        if res.get("warning"):
            st.warning("⚠️ " + res["warning"])
        elif res.get("mode") == "crewai":
            st.success("🤖 Investigated by a CrewAI crew. Open the Crew Briefing tab for the LLM summary.")
        st.markdown(ui.kpis(res, case), unsafe_allow_html=True)
    else:
        st.markdown('<div class="gg-note">👈 Fill in the case on the left, then press '
                    '<b>Launch investigation</b>.</div>', unsafe_allow_html=True)

res, case = st.session_state.get("result"), st.session_state.get("case")
EMPTY = '<div class="gg-note">🕵️ No investigation yet. Launch one from the first tab.</div>'

# ---------------------------------------------------------------- trace
with tab_trace:
    if not res:
        st.markdown(EMPTY, unsafe_allow_html=True)
    else:
        for t in res["trace"]:
            st.markdown(ui.agent_card(t), unsafe_allow_html=True)
            with st.expander(f"🔬 Raw data · {t['agent']}"):
                st.json(t["finding"].data)

# ---------------------------------------------------------------- analytics
with tab_stats:
    if not res:
        st.markdown(EMPTY, unsafe_allow_html=True)
    else:
        by = {t["agent"]: t["finding"] for t in res["trace"]}
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown('<div class="gg-panel"><h4>🎯 Case strength</h4>'
                        + ui.gauge(res["ctx"].get("case_strength", 0)) + "</div>", unsafe_allow_html=True)
        with c2:
            ranked = (by["Grid Analyst"].data or {}).get("ranked", [])
            st.markdown(ui.bars(ranked, "Likely cause of outage", "📡"), unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            ba = by["Bill Auditor"].data or {}
            if ba.get("expected") and case["billed"]:
                st.markdown(ui.bill_compare(ba["expected"], case["billed"]), unsafe_allow_html=True)
            else:
                st.markdown('<div class="gg-note">🧾 Enter units and billed amount to see the bill audit.</div>',
                            unsafe_allow_html=True)
        with c4:
            st.markdown(ui.confidence_bars(res["trace"]), unsafe_allow_html=True)
        notes = (by["Regulation Agent"].data or {}).get("notes", [])
        if notes:
            st.markdown('<div class="gg-panel"><h4>⚖️ Regulatory notes</h4>'
                        + "".join(f"<div>📌 {n}</div>" for n in notes) + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- complaint & approval
with tab_act:
    if not res:
        st.markdown(EMPTY, unsafe_allow_html=True)
    else:
        ctx = res["ctx"]
        st.markdown("### 🧑‍⚖️ Human approval")
        draft = st.text_area("✏️ Review / edit complaint", ctx["draft"]["en"], height=280)
        st.text_area("🗣️ Roman Urdu summary", ctx["draft"]["ur"], height=90)
        c1, c2 = st.columns(2)
        if c1.button("✅ Approve", use_container_width=True):
            Orchestrator.approve(res, True, draft)
        if c2.button("❌ Reject", use_container_width=True):
            Orchestrator.approve(res, False)
        badge = {"APPROVED": "success", "REJECTED": "error"}.get(res["status"], "info")
        getattr(st, badge)(f"📌 Status: {res['status']}")
        if res["status"] == "APPROVED":
            st.download_button("⬇️ Download complaint", ctx["draft"]["en"], "gridguard_complaint.txt")
            st.markdown("**🪜 Next: submit via** " + " → ".join(ctx["escalation"]))

# ---------------------------------------------------------------- crew briefing
with tab_brief:
    if not res:
        st.markdown(EMPTY, unsafe_allow_html=True)
    elif res.get("crew_report"):
        st.markdown("### 🤖 Case Officer briefing (CrewAI)")
        st.markdown(ui.briefing(res["crew_report"]), unsafe_allow_html=True)
    else:
        st.markdown('<div class="gg-note">🤖 No CrewAI briefing for this run. Choose <b>CrewAI crew (LLM)</b> '
                    'in the sidebar, add an API key, and launch again.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- about
with tab_about:
    st.markdown("""
### ℹ️ How GridGuard works
**🛰️ Pipeline:** 📍 Location → 🧾 Bill Auditor → 🔌 Outage Detector → 🌡️ Weather → ⚖️ Regulation →
📡 Grid Analyst → 🕵️ Evidence → ✍️ Action → 🧑‍⚖️ Human approval

**🤖 CrewAI mode:** every specialist is a real CrewAI agent with its own tool, running in a sequential crew,
plus a Case Officer agent that writes the final briefing. If CrewAI or the API key is missing, the app
falls back to the deterministic rules engine automatically.

**⚠️ Note:** tariff slabs and outage allowances are *illustrative*. Verify against NEPRA / DISCO notifications
before filing.
""")
