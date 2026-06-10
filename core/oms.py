import uuid
from data.database import get_session
from data.models import Order

class OrderManager:
    async def create_order(self, ticker, side, quantity):
        async with get_session() as session:
            order = Order(order_ref=str(uuid.uuid4()), side=side, quantity=quantity, status="NEW")
            session.add(order)
            await session.commit()
            return order.order_ref
oms = OrderManager()
