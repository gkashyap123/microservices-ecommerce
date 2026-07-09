import json
from fastapi import HTTPException
from core.redis import redis
from core.config import settings
from schemas.cart import CartItem, CartItemResponse, CartResponse, AddItemRequest, UpdateItemRequest

CART_KEY = "cart:{user_id}"     # key template

class CartService:
    def __init__(self, redis: redis.Redis):
        self.redis = redis

    # ── Private Helpers ──────────────────────────────────────────────

    def _key(self, user_id: str) -> str:
        """Builds the Redis key for a user's cart."""
        return CART_KEY.format(user_id=user_id)

    def _get_raw_items(self, user_id: str) -> dict:
        """Returns all raw hash fields for a cart."""
        return self.redis.hgetall(self._key(user_id))

    def _parse_items(self, raw: dict) -> list[CartItem]:
        """Deserializes all cart items from Redis hash."""
        return [CartItem(**json.loads(value)) for value in raw.values()]

    def _refresh_ttl(self, user_id: str):
        """Resets expiry on every cart interaction."""
        self.redis.expire(self._key(user_id), settings.CART_TTL_SECONDS)

    def _build_response(self, user_id: str, items: list[CartItem]) -> CartResponse:
        """Builds the full cart response with totals."""
        item_responses = [
            CartItemResponse(
                product_id=item.product_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                subtotal=round(item.price * item.quantity, 2),
            )
            for item in items
        ]

        ttl = self.redis.ttl(self._key(user_id))

        return CartResponse(
            user_id=user_id,
            items=item_responses,
            total_items=sum(i.quantity for i in items),
            total_price=round(sum(i.price * i.quantity for i in items), 2),
            ttl_seconds=ttl if ttl > 0 else None,
        )

    # ── Public Methods ────────────────────────────────────────────────

    def get_cart(self, user_id: str) -> CartResponse:
        raw = self._get_raw_items(user_id)
        items = self._parse_items(raw)
        return self._build_response(user_id, items)

    def add_item(self, user_id: str, payload: AddItemRequest) -> CartResponse:
        key = self._key(user_id)
        field = str(payload.product_id)

        # If item already exists → increment quantity
        existing_raw = self.redis.hget(key, field)
        if existing_raw:
            existing = CartItem(**json.loads(existing_raw))
            existing.quantity += payload.quantity
            item = existing
        else:
            item = CartItem(
                product_id=payload.product_id,
                name=payload.name,
                price=payload.price,
                quantity=payload.quantity,
            )

        self.redis.hset(key, field, json.dumps(item.model_dump()))
        self._refresh_ttl(user_id)

        return self.get_cart(user_id)

    def update_item(self, user_id: str, product_id: int, payload: UpdateItemRequest) -> CartResponse:
        key = self._key(user_id)
        field = str(product_id)

        existing_raw = self.redis.hget(key, field)
        if not existing_raw:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        item = CartItem(**json.loads(existing_raw))
        item.quantity = payload.quantity

        self.redis.hset(key, field, json.dumps(item.model_dump()))
        self._refresh_ttl(user_id)

        return self.get_cart(user_id)

    def remove_item(self, user_id: str, product_id: int) -> CartResponse:
        key = self._key(user_id)
        field = str(product_id)

        if not self.redis.hexists(key, field):
            raise HTTPException(status_code=404, detail="Item not found in cart")

        self.redis.hdel(key, field)
        self._refresh_ttl(user_id)

        return self.get_cart(user_id)

    def clear_cart(self, user_id: str) -> dict:
        self.redis.delete(self._key(user_id))
        return {"message": f"Cart cleared for user {user_id}"}

    def get_item_count(self, user_id: str) -> dict:
        raw = self._get_raw_items(user_id)
        items = self._parse_items(raw)
        return {
            "user_id": user_id,
            "total_items": sum(i.quantity for i in items),
            "unique_products": len(items),
        }