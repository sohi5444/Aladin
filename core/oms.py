import uuid
from data.models import Order, Instrument

class OrderManager:
    async def create_order(self, ticker: str, side: str, quantity: float, limit_price=None) -> str:
        instr = Instrument.get_or_create(ticker)
        order_ref = str(uuid.uuid4())
        Order.create(
            order_ref=order_ref,
            instrument_id=instr["id"],
            side=side.upper(),
            quantity=quantity,
            status="NEW",
            limit_price=limit_price
        )
        return order_ref

    async def get_orders(self):
        return Order.all()

oms = OrderManager()
