import random
from data.models import RiskSnapshot

class RiskEngine:
    async def take_snapshot(self):
        var_95 = round(random.uniform(0.5, 3.5), 2)
        RiskSnapshot.create(var_95=var_95)
        return var_95

    async def stress_test(self, scenario: str):
        return {"scenario": scenario, "loss_pct": round(random.uniform(5, 20), 1)}

risk_engine = RiskEngine()
