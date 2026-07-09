import asyncio
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.order_repository import OrderRepository
from clients.cart_client import CartClient
from clients.product_client import ProductClient
from models.order import OrderStatus
from schemas.order import UpdateStatusRequest, PlaceOrderRequest
from core.rabbitmq import publish_order_event


class OrderService:
    def __init__(self, db: Session):
        self.repo         = OrderRepository(db)
        self.cart_client  = CartClient()
        self.product_client = ProductClient()

    # ── Place Order ───────────────────────────────────────────────────

    async def place_order(self, user_id: str, payload: PlaceOrderRequest):
        order = None
        try:
            # Step 1 — Fetch cart
            cart = await self.cart_client.get_cart(user_id)
            if not cart.items:
                raise HTTPException(status_code=400, detail="Cart is empty")

            # Step 2 — Validate all products
            await self.product_client.validate_products(
                [{"product_id": i.product_id, "quantity": i.quantity}
                 for i in cart.items]
            )

            # Step 3 — Create order (PENDING)
            order = self.repo.create(
                user_id=user_id,
                total_price=cart.total_price,
                items=[i.model_dump() for i in cart.items],
            )
            # ✅ order.id is now available here

            # Step 4 — Deduct stock
            for item in cart.items:
                await self.product_client.deduct_stock(
                    item.product_id, item.quantity
                )

            # Step 5 — Clear cart
            await self.cart_client.clear_cart(user_id)

            # Step 6 — Mark CONFIRMED
            confirmed_order = self.repo.update_status(order, OrderStatus.CONFIRMED)
            # ✅ confirmed_order.id, confirmed_order.items all available here

            # Step 7 — Publish event to RabbitMQ
            await publish_order_event({
                "event_type": "order.confirmed",
                "order_id": confirmed_order.id,          # ✅ from confirmed_order
                "user_id": user_id,                      # ✅ from parameter
                "user_email": payload.user_email,        # ✅ from request payload
                "user_phone": payload.user_phone,        # ✅ from request payload
                "status": "CONFIRMED",
                "total_price": confirmed_order.total_price,
                "items": [
                    {
                        "product_id": i.product_id,
                        "name": i.name,
                        "price": i.price,
                        "quantity": i.quantity,
                        "subtotal": i.subtotal,
                    }
                    for i in confirmed_order.items       # ✅ items loaded via joinedload
                ],
            })

            return confirmed_order

        except HTTPException:
            if order:
                self.repo.update_status(order, OrderStatus.FAILED)

                # Publish FAILED event too
                await publish_order_event({
                    "event_type": "order.failed",
                    "order_id": order.id,
                    "user_id": user_id,
                    "user_email": payload.user_email,
                    "user_phone": payload.user_phone,
                    "status": "FAILED",
                    "total_price": order.total_price,
                    "failure_reason": "Stock unavailable or validation failed",
                    "items": [
                        {
                            "product_id": i.product_id,
                            "name": i.name,
                            "price": i.price,
                            "quantity": i.quantity,
                            "subtotal": i.subtotal,
                        }
                        for i in order.items
                    ],
                })
            raise

        except Exception as e:
            if order:
                self.repo.update_status(order, OrderStatus.FAILED)
            raise HTTPException(
                status_code=500,
                detail=f"Order failed: {str(e)}"
            )

    # ── Read ──────────────────────────────────────────────────────────

    def get_user_orders(self, user_id: str, page: int, page_size: int) -> dict:
        orders, total = self.repo.get_all_by_user(user_id, page, page_size)
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": orders,
        }

    def get_order_by_id(self, order_id: int):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    # ── Status Update ─────────────────────────────────────────────────

    def update_status(self, order_id: int, payload: UpdateStatusRequest):
        order = self.get_order_by_id(order_id)

        invalid = {
            OrderStatus.DELIVERED: "Order already delivered",
            OrderStatus.CANCELLED: "Order already cancelled",
            OrderStatus.FAILED:    "Cannot update a failed order",
        }
        if order.status in invalid:
            raise HTTPException(status_code=400, detail=invalid[order.status])

        return self.repo.update_status(order, payload.status)

    # ── Cancel ────────────────────────────────────────────────────────

    def cancel_order(self, order_id: int):
        order = self.get_order_by_id(order_id)

        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel order with status '{order.status}'"
            )

        return self.repo.update_status(order, OrderStatus.CANCELLED)