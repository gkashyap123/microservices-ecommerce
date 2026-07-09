from sqlalchemy.orm import Session, joinedload
from models.order import Order, OrderStatus
from models.order_item import OrderItem

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[Order], int]:
        query = (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        total = query.count()
        orders = query.offset((page - 1) * page_size).limit(page_size).all()
        return orders, total

    def get_by_id(self, order_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.id == order_id)
            .first()
        )

    def create(self, user_id: str, total_price: float, items: list[dict]) -> Order:
        order = Order(user_id=user_id, total_price=total_price)
        self.db.add(order)
        self.db.flush()     # get order.id before committing

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"],
                subtotal=round(item["price"] * item["quantity"], 2),
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return self.get_by_id(order.id)

    def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete(self, order: Order) -> None:
        self.db.delete(order)
        self.db.commit()