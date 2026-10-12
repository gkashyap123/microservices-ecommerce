import os

import httpx


ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL",
    "http://localhost:8004",
)


async def get_order(order_id: int) -> dict:
    """
    Fetch an order from the existing Order Service.
    The Order Service remains the source of truth.
    """

    url = f"{ORDER_SERVICE_URL}/orders/{order_id}"

    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=10.0,
        pool=10.0,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:

        response = await client.get(url)

        response.raise_for_status()

        return response.json()


async def cancel_order(
    order_id: int,
) -> dict:

    url = (
        f"{ORDER_SERVICE_URL}"
        f"/orders/{order_id}/cancel"
    )

    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=10.0,
        pool=10.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        response = await client.patch(
            url
        )

        response.raise_for_status()

        return response.json()