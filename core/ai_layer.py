class AIAssistant:
    async def generate_daily_briefing(self, macro, risk, portfolio):
        return f"Regime: {macro['regime']}. VaR: {risk.var_95}%"
ai = AIAssistant()
