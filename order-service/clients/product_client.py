import httpx
from fastapi import HTTPException
from core.config import settings
from schemas.order import ProductData

BASE_URL = settings.PRODUCT_SERVICE_URL

class ProductClient:

    async def get_product(self, product_id: int) -> ProductData:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BASE_URL}/products/{product_id}")
                response.raise_for_status()
                return ProductData(**response.json())
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Product service error: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Product service is unavailable"
                )

    async def deduct_stock(self, product_id: int, quantity: int) -> None:
        """Reduces stock by sending updated quantity via PUT."""
        product = await self.get_product(product_id)

        new_stock = product.stock - quantity
        if new_stock < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'. "
                       f"Available: {product.stock}, Requested: {quantity}"
            )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{BASE_URL}/products/{product_id}",
                    json={"stock": new_stock}
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Failed to deduct stock: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Product service unavailable during stock deduction"
                )

    async def validate_products(self, items: list[dict]) -> list[ProductData]:
        """Validates all cart items — active, sufficient stock, correct price."""
        validated = []
        for item in items:
            product = await self.get_product(item["product_id"])

            if not product.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product '{product.name}' is no longer available"
                )

            if product.stock < item["quantity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for '{product.name}'. "
                           f"Available: {product.stock}, Requested: {item['quantity']}"
                )

            validated.append(product)

        return validated