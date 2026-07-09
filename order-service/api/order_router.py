from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.order import OrderResponse, OrderListResponse, UpdateStatusRequest
from services.order_service import OrderService
from schemas.order import PlaceOrderRequest
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/{user_id}", response_model=OrderResponse, status_code=201)
async def place_order(user_id: str, payload: PlaceOrderRequest, db: Session = Depends(get_db)):
    return await OrderService(db).place_order(user_id,payload)


@router.get("/user/{user_id}", response_model=OrderListResponse)
def get_user_orders(
    user_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return OrderService(db).get_user_orders(user_id, page, page_size)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return OrderService(db).get_order_by_id(order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    payload: UpdateStatusRequest,
    db: Session = Depends(get_db),
):
    return OrderService(db).update_status(order_id, payload)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    return OrderService(db).cancel_order(order_id)