class ComplianceEngine:
    async def pre_trade_check(self, order):
        return True, "OK"
compliance_engine = ComplianceEngine()
