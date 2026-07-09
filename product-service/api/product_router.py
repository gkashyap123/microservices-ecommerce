from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=ProductListResponse)
def get_all(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    category_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    db: Session = Depends(get_db),
):
    return ProductService(db).get_all(
        page, page_size, category_id, search, min_price, max_price
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_one(product_id: int, db: Session = Depends(get_db)):
    return ProductService(db).get_by_id(product_id)

@router.post("/", response_model=ProductResponse, status_code=201)
def create(payload: ProductCreate, db: Session = Depends(get_db)):
    return ProductService(db).create(payload)

@router.put("/{product_id}", response_model=ProductResponse)
def update(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    return ProductService(db).update(product_id, payload)

@router.delete("/{product_id}")
def delete(product_id: int, db: Session = Depends(get_db)):
    return ProductService(db).delete(product_id)