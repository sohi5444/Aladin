import random

class MacroBrain:
    async def get_dashboard(self):
        regimes = ["Risk On", "Risk Off", "Stagflation"]
        return {
            "regime": random.choice(regimes),
            "surprise_index": round(random.uniform(-1, 1), 2),
            "fed_rate_implied": round(random.uniform(4.5, 5.5), 2)
        }
macro = MacroBrain()
