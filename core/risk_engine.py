import random
from data.models import RiskSnapshot
from data.database import get_session

class RiskEngine:
    async def take_snapshot(self):
        snapshot = RiskSnapshot(var_95=round(random.uniform(0.5, 2.0), 2))
        async with get_session() as session:
            session.add(snapshot)
            await session.commit()
        return snapshot

    async def stress_test(self, scenario: str):
        return {"scenario": scenario, "loss_pct": random.uniform(5, 20)}
risk_engine = RiskEngine()
