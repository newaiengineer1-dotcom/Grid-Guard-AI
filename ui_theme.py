"""Premium themes + CSS for the GridGuard AI dashboard."""

THEMES = {
    "🌌 Midnight Neon": dict(bg1="#050816", bg2="#0b1030", card="rgba(18,26,60,.62)", line="rgba(120,160,255,.18)",
                             a1="#22d3ee", a2="#8b5cf6", text="#e6ecff", muted="#8f9bc7", glow="rgba(34,211,238,.35)"),
    "🌿 Aurora Emerald": dict(bg1="#041510", bg2="#082a22", card="rgba(10,48,40,.60)", line="rgba(110,231,183,.20)",
                              a1="#34d399", a2="#22d3ee", text="#e8fff6", muted="#8fc7b4", glow="rgba(52,211,153,.35)"),
    "👑 Royal Gold": dict(bg1="#0b0906", bg2="#1a140a", card="rgba(38,30,14,.62)", line="rgba(251,191,36,.22)",
                          a1="#fbbf24", a2="#f97316", text="#fff7e0", muted="#c9b27a", glow="rgba(251,191,36,.35)"),
    "🔥 Crimson Grid": dict(bg1="#12050a", bg2="#2a0a14", card="rgba(52,14,26,.62)", line="rgba(251,113,133,.22)",
                            a1="#fb7185", a2="#f59e0b", text="#ffe8ec", muted="#c995a0", glow="rgba(251,113,133,.35)"),
    "🌊 Ocean Glass": dict(bg1="#04101c", bg2="#0a2540", card="rgba(14,44,76,.60)", line="rgba(125,211,252,.22)",
                           a1="#38bdf8", a2="#6366f1", text="#e6f4ff", muted="#8fb4d4", glow="rgba(56,189,248,.35)"),
}

AGENT_ICONS = {
    "Location Agent": "📍", "Bill Auditor": "🧾", "Outage Detector": "🔌", "Weather / Environment Agent": "🌡️",
    "Regulation Agent": "⚖️", "Grid Analyst": "📡", "Investigation / Evidence Agent": "🕵️", "Action Agent": "✍️",
}
SEV = {"info": ("🟢", "OK"), "warn": ("🟠", "WARN"), "critical": ("🔴", "CRITICAL")}


def css(t: dict) -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {{ --a1:{t['a1']}; --a2:{t['a2']}; --card:{t['card']}; --line:{t['line']}; --text:{t['text']};
         --muted:{t['muted']}; --glow:{t['glow']}; }}
html, body, [class*="css"], .stApp {{ font-family:'Inter',system-ui,sans-serif; color:var(--text); }}
.stApp {{ background: radial-gradient(1200px 600px at 10% -10%, {t['bg2']} 0%, transparent 60%),
          radial-gradient(900px 500px at 100% 0%, {t['glow']} 0%, transparent 55%), {t['bg1']}; }}
#MainMenu, footer {{ visibility:hidden; }}
header[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ padding-top:1.4rem; max-width:1250px; }}
section[data-testid="stSidebar"] {{ background:linear-gradient(180deg,{t['bg2']},{t['bg1']});
          border-right:1px solid var(--line); }}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3 {{ color:var(--a1); }}

.gg-hero {{ position:relative; overflow:hidden; border:1px solid var(--line); border-radius:22px; padding:26px 30px;
  background:linear-gradient(135deg,var(--card),rgba(0,0,0,.25)); backdrop-filter:blur(14px);
  box-shadow:0 10px 40px rgba(0,0,0,.45), 0 0 60px var(--glow) inset; margin-bottom:14px; }}
.gg-hero:before {{ content:""; position:absolute; inset:-40% auto auto 60%; width:420px; height:420px; border-radius:50%;
  background:radial-gradient(circle,var(--glow),transparent 70%); filter:blur(10px); }}
.gg-hero h1 {{ margin:0; font-size:2.3rem; font-weight:800; letter-spacing:-.5px;
  background:linear-gradient(90deg,var(--a1),var(--a2)); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.gg-hero p {{ margin:.35rem 0 0; color:var(--muted); font-size:1rem; }}
.gg-badges {{ margin-top:12px; display:flex; flex-wrap:wrap; gap:8px; position:relative; }}
.gg-chip {{ display:inline-flex; align-items:center; gap:6px; padding:5px 12px; border-radius:999px; font-size:.78rem;
  font-weight:600; border:1px solid var(--line); background:rgba(255,255,255,.04); color:var(--text); }}
.gg-chip.on {{ border-color:var(--a1); box-shadow:0 0 14px var(--glow); }}

.gg-kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:10px 0 18px; }}
.gg-kpi {{ border:1px solid var(--line); border-radius:18px; padding:16px 18px; background:var(--card);
  backdrop-filter:blur(10px); box-shadow:0 6px 24px rgba(0,0,0,.35); transition:transform .2s, box-shadow .2s; }}
.gg-kpi:hover {{ transform:translateY(-3px); box-shadow:0 12px 32px rgba(0,0,0,.5), 0 0 24px var(--glow); }}
.gg-kpi .ic {{ font-size:1.5rem; }}
.gg-kpi .lb {{ color:var(--muted); font-size:.72rem; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-top:6px; }}
.gg-kpi .vl {{ font-size:1.7rem; font-weight:800; margin-top:2px;
  background:linear-gradient(90deg,var(--a1),var(--a2)); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.gg-kpi .sb {{ color:var(--muted); font-size:.78rem; margin-top:2px; }}

.gg-panel {{ border:1px solid var(--line); border-radius:18px; padding:18px 20px; background:var(--card);
  backdrop-filter:blur(10px); margin-bottom:14px; }}
.gg-panel h4 {{ margin:0 0 12px; font-size:1rem; font-weight:700; }}

.gg-steps {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(118px,1fr)); gap:10px; }}
.gg-step {{ text-align:center; padding:12px 6px; border-radius:14px; border:1px solid var(--line);
  background:rgba(255,255,255,.03); font-size:.74rem; color:var(--muted); }}
.gg-step .si {{ font-size:1.5rem; display:block; margin-bottom:4px; filter:grayscale(1) opacity(.5); }}
.gg-step.done {{ color:var(--text); border-color:var(--a1); box-shadow:0 0 16px var(--glow); }}
.gg-step.done .si {{ filter:none; }}
.gg-step.run {{ border-color:var(--a2); animation:pulse 1s infinite; }}
@keyframes pulse {{ 50% {{ box-shadow:0 0 22px var(--glow); }} }}

.gg-agent {{ display:flex; gap:14px; align-items:flex-start; border:1px solid var(--line); border-radius:16px;
  padding:14px 16px; margin-bottom:10px; background:var(--card); border-left:4px solid var(--a1); }}
.gg-agent.warn {{ border-left-color:#f59e0b; }} .gg-agent.critical {{ border-left-color:#ef4444; }}
.gg-agent .ai {{ font-size:1.8rem; line-height:1; }}
.gg-agent .an {{ font-weight:700; }} .gg-agent .as {{ color:var(--muted); font-size:.9rem; margin-top:2px; }}
.gg-agent .am {{ margin-left:auto; text-align:right; font-size:.72rem; color:var(--muted); white-space:nowrap; }}
.gg-pill {{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:.68rem; font-weight:700; margin-bottom:4px;
  border:1px solid var(--line); }}
.gg-pill.info {{ color:#34d399; }} .gg-pill.warn {{ color:#f59e0b; }} .gg-pill.critical {{ color:#ef4444; }}

.gg-gauge {{ --p:0; width:170px; height:170px; border-radius:50%; margin:6px auto; display:grid; place-items:center;
  background:conic-gradient(var(--a1) calc(var(--p)*1%), rgba(255,255,255,.08) 0); box-shadow:0 0 34px var(--glow); }}
.gg-gauge .in {{ width:132px; height:132px; border-radius:50%; background:{t['bg1']}; display:grid; place-items:center; text-align:center; }}
.gg-gauge .n {{ font-size:2rem; font-weight:800; }} .gg-gauge .l {{ font-size:.7rem; color:var(--muted); letter-spacing:1px; }}

.gg-bar {{ margin:9px 0; }} .gg-bar .t {{ display:flex; justify-content:space-between; font-size:.84rem; margin-bottom:4px; }}
.gg-bar .tr {{ height:10px; border-radius:99px; background:rgba(255,255,255,.08); overflow:hidden; }}
.gg-bar .fi {{ height:100%; border-radius:99px; background:linear-gradient(90deg,var(--a1),var(--a2)); box-shadow:0 0 12px var(--glow); }}

.gg-note {{ border:1px dashed var(--line); border-radius:14px; padding:10px 14px; color:var(--muted); font-size:.85rem; }}
.gg-brief {{ border:1px solid var(--a2); border-radius:16px; padding:16px 18px; background:rgba(255,255,255,.04); line-height:1.6; }}

/* Streamlit widgets */
.stTabs [data-baseweb="tab-list"] {{ gap:6px; background:var(--card); padding:6px; border-radius:16px; border:1px solid var(--line); }}
.stTabs [data-baseweb="tab"] {{ height:44px; border-radius:12px; padding:0 18px; font-weight:600; color:var(--muted); }}
.stTabs [aria-selected="true"] {{ background:linear-gradient(90deg,var(--a1),var(--a2)); color:#04101c !important; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display:none; }}
.stButton>button, .stDownloadButton>button {{ border-radius:12px; font-weight:700; border:1px solid var(--line);
  transition:all .2s; }}
.stButton>button[kind="primary"] {{ background:linear-gradient(90deg,var(--a1),var(--a2)); color:#04101c; border:none;
  box-shadow:0 6px 22px var(--glow); }}
.stButton>button:hover, .stDownloadButton>button:hover {{ transform:translateY(-2px); box-shadow:0 8px 24px var(--glow); }}
.stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"]>div {{
  border-radius:12px !important; background:rgba(255,255,255,.04) !important; border:1px solid var(--line) !important; }}
div[data-testid="stExpander"] {{ border:1px solid var(--line); border-radius:14px; background:var(--card); }}
</style>
"""
