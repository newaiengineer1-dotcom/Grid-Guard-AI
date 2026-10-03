from .base import Agent, Finding

# ILLUSTRATIVE slab rates (Rs/unit). Update from the latest NEPRA/DISCO tariff notification.
SLABS = [(100, 7.5), (200, 10.5), (300, 20.0), (400, 26.0), (700, 30.0), (10**9, 36.0)]
GST, FPA_PER_UNIT = 0.18, 1.5


def expected_bill(units: float) -> float:
    rate = next(r for cap, r in SLABS if units <= cap)
    return round((units * rate + units * FPA_PER_UNIT) * (1 + GST), 2)


class BillAuditor(Agent):
    name = "Bill Auditor"

    def run(self, case, ctx):
        u, billed, prev = case.get("units", 0), case.get("billed", 0), case.get("prev_units", 0)
        if not u or not billed:
            return Finding(self.name, "No bill data supplied; audit skipped.", "info", 0.2)
        exp = expected_bill(u)
        var = (billed - exp) / exp
        flags = []
        if var > 0.15:
            flags.append(f"Billed Rs {billed:,.0f} is {var:.0%} above expected Rs {exp:,.0f}.")
        if prev and u > prev * 1.5:
            flags.append(f"Units jumped {u/prev - 1:.0%} vs last month ({prev:.0f} to {u:.0f}); check meter reading / estimated billing.")
        if u > 200 and prev and prev <= 200:
            flags.append("Crossed 200 units: protected-consumer status and slab rate may have changed.")
        sev = "critical" if var > 0.3 else "warn" if flags else "info"
        return Finding(self.name, " ".join(flags) or "Bill is consistent with the configured tariff.", sev,
                       0.75 if flags else 0.6, {"expected": exp, "variance": round(var, 3), "flags": flags})
