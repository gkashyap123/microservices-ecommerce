import httpx
from fastapi import HTTPException
from core.config import settings
from schemas.order import CartData

BASE_URL = settings.CART_SERVICE_URL

class CartClient:

    async def get_cart(self, user_id: str) -> CartData:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BASE_URL}/cart/{user_id}")
                response.raise_for_status()
                return CartData(**response.json())
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Cart service error: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Cart service is unavailable"
                )

    async def clear_cart(self, user_id: str) -> None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(f"{BASE_URL}/cart/{user_id}")
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Log but don't fail the order — cart clear is non-critical
                print(f"Warning: Failed to clear cart for {user_id}: {e}")
            except httpx.RequestError:
                print(f"Warning: Cart service unavailable when clearing cart for {user_id}")