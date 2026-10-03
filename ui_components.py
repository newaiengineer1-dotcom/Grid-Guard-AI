"""Small HTML renderers for the dashboard (kept dependency-free)."""
from html import escape

from ui_theme import AGENT_ICONS, SEV

AGENT_ORDER = list(AGENT_ICONS)


def _h(s: str) -> str:
    # Streamlit markdown treats 4+ leading spaces as a code block, so flatten the HTML.
    return "".join(line.strip() for line in s.splitlines())


def hero(mode: str, crew_ok: bool) -> str:
    crew = "🤖 CrewAI ready" if crew_ok else "🤖 CrewAI not installed"
    return _h(f"""
<div class="gg-hero">
  <h1>⚡ GridGuard AI</h1>
  <p>Autonomous multi-agent incident response for Pakistan's electricity outages and billing disputes.
     🛡️ Nothing is filed without your approval.</p>
  <div class="gg-badges">
    <span class="gg-chip on">🧠 {escape(mode)}</span>
    <span class="gg-chip {'on' if crew_ok else ''}">{crew}</span>
    <span class="gg-chip">🇵🇰 11 cities · 10 DISCOs</span>
    <span class="gg-chip">🗣️ Urdu · Roman Urdu · English</span>
  </div>
</div>""")


def kpis(res: dict, case: dict) -> str:
    ctx, trace = res["ctx"], {t["agent"]: t["finding"] for t in res["trace"]}
    ba = trace.get("Bill Auditor")
    exp = (ba.data or {}).get("expected") if ba else None
    var = (ba.data or {}).get("variance") if ba else None
    ev = trace.get("Investigation / Evidence Agent")
    verdict = (ev.data or {}).get("verdict", "-") if ev else "-"
    cards = [
        ("🎯", "Case strength", f"{ctx.get('case_strength', 0):.0%}", f"Verdict: {verdict}"),
        ("🏢", "Your DISCO", ctx.get("disco", "n/a"), case.get("city", "")),
        ("🔌", "Outage", f"{ctx.get('outage_hours', 0):g} h", f"Excess over schedule: {ctx.get('excess_hours', 0):g} h"),
        ("🧾", "Bill variance", f"{var:+.0%}" if var is not None else "n/a",
         f"Expected Rs {exp:,.0f}" if exp else "No bill data"),
        ("🌡️", "Weather", f"{ctx.get('temp_c', '-')}°C", f"Wind {ctx.get('wind_kmh', 0)} km/h"),
    ]
    body = "".join(f'<div class="gg-kpi"><div class="ic">{i}</div><div class="lb">{l}</div>'
                   f'<div class="vl">{escape(str(v))}</div><div class="sb">{escape(str(s))}</div></div>'
                   for i, l, v, s in cards)
    return _h(f'<div class="gg-kpis">{body}</div>')


def stepper(done: set, running: str | None = None) -> str:
    short = {"Weather / Environment Agent": "Weather", "Investigation / Evidence Agent": "Evidence"}
    out = []
    for n in AGENT_ORDER:
        cls = "done" if n in done else "run" if n == running else ""
        out.append(f'<div class="gg-step {cls}"><span class="si">{AGENT_ICONS[n]}</span>'
                   f'{escape(short.get(n, n.replace(" Agent", "")))}</div>')
    return _h(f'<div class="gg-panel"><h4>🛰️ Agent pipeline</h4><div class="gg-steps">{"".join(out)}</div></div>')


def agent_card(t: dict) -> str:
    f = t["finding"]
    dot, label = SEV[f.severity]
    return _h(f"""
<div class="gg-agent {f.severity}">
  <div class="ai">{AGENT_ICONS.get(t['agent'], '🤖')}</div>
  <div><div class="an">{escape(t['agent'])}</div><div class="as">{escape(f.summary)}</div></div>
  <div class="am"><span class="gg-pill {f.severity}">{dot} {label}</span><br>
     ⏱️ {t['ms']} ms<br>📶 {f.confidence:.0%} confidence</div>
</div>""")


def gauge(score: float, label: str = "CASE STRENGTH") -> str:
    return _h(f'<div class="gg-gauge" style="--p:{score * 100:.0f}"><div class="in"><div>'
              f'<div class="n">{score:.0%}</div><div class="l">{label}</div></div></div></div>')


def bars(items, title: str, icon: str = "📊") -> str:
    rows = "".join(f'<div class="gg-bar"><div class="t"><span>{escape(n)}</span><b>{v:.0%}</b></div>'
                   f'<div class="tr"><div class="fi" style="width:{min(max(v, 0), 1) * 100:.0f}%"></div></div></div>'
                   for n, v in items)
    return _h(f'<div class="gg-panel"><h4>{icon} {escape(title)}</h4>{rows}</div>')


def bill_compare(expected: float, billed: float) -> str:
    top = max(expected, billed, 1)
    rows = bars([("Expected (tariff model)", expected / top), ("Billed", billed / top)], "Bill vs expected", "🧾")
    return rows + _h(f'<div class="gg-note">Expected Rs {expected:,.0f} · Billed Rs {billed:,.0f} · '
                     f'Difference Rs {billed - expected:+,.0f}</div>')


def confidence_bars(trace) -> str:
    return bars([(t["agent"], t["finding"].confidence) for t in trace], "Confidence by agent", "📶")


def briefing(text: str) -> str:
    return _h(f'<div class="gg-brief">🧠 {escape(text).replace(chr(10), "<br>")}</div>')
