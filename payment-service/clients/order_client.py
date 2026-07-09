import httpx
from core.config import settings

class OrderClient:

    async def update_order_status(self, order_id: int, status: str) -> None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{settings.ORDER_SERVICE_URL}/orders/{order_id}/status",
                    json={"status": status},
                )
                response.raise_for_status()
                print(f"Order #{order_id} updated to {status}")
            except httpx.HTTPStatusError as e:
                # Non-critical — log and continue
                print(f"Warning: order-service returned error for "
                      f"order #{order_id}: {e.response.text}")
            except httpx.RequestError:
                print(f"Warning: order-service unreachable "
                      f"for order #{order_id}")