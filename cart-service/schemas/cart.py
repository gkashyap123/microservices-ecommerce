from pydantic import BaseModel, Field
from typing import Optional

# --- Request Schemas ---

class AddItemRequest(BaseModel):
    product_id: int
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=1, default=1)

class UpdateItemRequest(BaseModel):
    quantity: int = Field(ge=1)

# --- Internal / Storage Schema ---

class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return round(self.price * self.quantity, 2)

# --- Response Schemas ---

class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

class CartResponse(BaseModel):
    user_id: str
    items: list[CartItemResponse]
    total_items: int            # total quantity across all products
    total_price: float          # grand total
    ttl_seconds: Optional[int]  # seconds until cart expires