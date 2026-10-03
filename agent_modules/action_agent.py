from datetime import date
from .base import Agent, Finding


class ActionAgent(Agent):
    name = "Action Agent"

    def run(self, case, ctx):
        ev = [f"- {b}" for b in ctx.get("evidence", [])] or ["- See attached bill and outage log."]
        disco = ctx.get("disco", "the concerned DISCO")
        city = case.get("city", "").title()
        en = (f"Date: {date.today():%d %b %Y}\nTo: Complaint Cell, {disco} (cc: NEPRA)\n"
              f"Subject: Complaint - outages and billing, Consumer No. {case.get('consumer_no') or '__________'}\n\n"
              f"I am a consumer in {city}. I report {ctx.get('outage_hours', 0):g} hours of outage "
              f"(excess over schedule: {ctx.get('excess_hours', 0):g}h) and a disputed bill.\n\nFindings:\n" + "\n".join(ev) +
              "\n\nI request: (1) restoration and fault explanation, (2) bill re-verification with meter reading, "
              "(3) a written response within the prescribed time.\n\nRegards,\n" + (case.get("name") or "Consumer"))
        ur = (f"{disco} ko shikayat: {city} mein {ctx.get('outage_hours', 0):g} ghantay bijli ghayab rahi aur bill zyada aya hai. "
              "Barae meherbani bill ki dobara jaanch aur bijli ki bahali ka likhit jawab dein.")
        ctx["draft"] = {"en": en, "ur": ur}
        return Finding(self.name, "Complaint drafted. Awaiting human approval before anything is filed.", "info", 0.8, ctx["draft"])
