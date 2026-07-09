from pydantic import BaseModel, Field
from typing import Optional
from schemas.category import CategoryResponse

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock: int = Field(ge=0, default=0)
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_active: bool
    category_id: int
    category: CategoryResponse        # ← nested category in response

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[ProductResponse]    # ← paginated wrapper