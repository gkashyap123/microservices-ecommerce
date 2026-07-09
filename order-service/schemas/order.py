from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.order import OrderStatus

# --- Item Schemas ---

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True

# --- Order Schemas ---

class OrderResponse(BaseModel):
    id: int
    user_id: str
    status: OrderStatus
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime]
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True

class UpdateStatusRequest(BaseModel):
    status: OrderStatus

class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[OrderResponse]

# --- Internal schemas (inter-service communication) ---

class CartItemData(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

class CartData(BaseModel):
    user_id: str
    items: list[CartItemData]
    total_price: float

class ProductData(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    is_active: bool

class PlaceOrderRequest(BaseModel):
    user_email: str
    user_phone: str     # E.164 format e.g. "+919876543210"    