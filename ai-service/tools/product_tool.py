import os
from typing import Optional

import httpx


PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://localhost:8005",
)


async def search_products(
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:

    params = {
        "page": page,
        "page_size": page_size,
    }

    if search:
        params["search"] = search

    if min_price is not None:
        params["min_price"] = min_price

    if max_price is not None:
        params["max_price"] = max_price

    if category_id is not None:
        params["category_id"] = category_id

    url = f"{PRODUCT_SERVICE_URL}/products/"

    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=10.0,
        pool=10.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        response = await client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()


async def get_product(
    product_id: int,
) -> dict:

    url = (
        f"{PRODUCT_SERVICE_URL}"
        f"/products/{product_id}"
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

        response = await client.get(url)

        response.raise_for_status()

        return response.json()