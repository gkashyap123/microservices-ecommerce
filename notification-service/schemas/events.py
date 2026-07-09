from pydantic import BaseModel
from enum import Enum
from typing import Optional

class OrderStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    SHIPPED   = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED    = "FAILED"

class OrderItemEvent(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

class OrderEvent(BaseModel):
    event_type: str                  # "order.confirmed", "order.shipped" etc.
    order_id: int
    user_id: str
    user_email: str
    user_phone: str                  # E.164 format e.g. "+919876543210"
    status: OrderStatus
    total_price: float
    items: list[OrderItemEvent]
    failure_reason: Optional[str] = None   # only for FAILED events