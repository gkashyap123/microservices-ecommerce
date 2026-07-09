from fastapi import APIRouter, Depends
from redis import Redis
from core.redis import get_redis
from schemas.cart import AddItemRequest, UpdateItemRequest, CartResponse
from services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])

# Dependency — injects CartService with Redis into every route
def get_cart_service(redis: Redis = Depends(get_redis)) -> CartService:
    return CartService(redis)


@router.get("/{user_id}", response_model=CartResponse)
def get_cart(user_id: str, service: CartService = Depends(get_cart_service)):
    return service.get_cart(user_id)


@router.post("/{user_id}/items", response_model=CartResponse, status_code=201)
def add_item(
    user_id: str,
    payload: AddItemRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.add_item(user_id, payload)


@router.put("/{user_id}/items/{product_id}", response_model=CartResponse)
def update_item(
    user_id: str,
    product_id: int,
    payload: UpdateItemRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.update_item(user_id, product_id, payload)


@router.delete("/{user_id}/items/{product_id}", response_model=CartResponse)
def remove_item(
    user_id: str,
    product_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.remove_item(user_id, product_id)


@router.delete("/{user_id}", status_code=200)
def clear_cart(user_id: str, service: CartService = Depends(get_cart_service)):
    return service.clear_cart(user_id)


@router.get("/{user_id}/count")
def get_item_count(user_id: str, service: CartService = Depends(get_cart_service)):
    return service.get_item_count(user_id)