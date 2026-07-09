"""
Product Proxy
Forwards /products/* requests to the upstream product-service.
Public: GET (browsing catalogue)
Protected: POST / PUT / PATCH / DELETE (admin mutations)
"""
import httpx
import json
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body

from core.config import get_settings, Settings
from core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


async def _proxy(request: Request, settings: Settings, payload: dict | None = None) -> Response:
    url = f"{settings.PRODUCT_SERVICE_URL}{request.url.path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    else:
        body = await request.body()

    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    if payload is not None and "content-type" not in {k.lower() for k in headers.keys()}:
        headers["content-type"] = "application/json"

    timeout = httpx.Timeout(
        connect=settings.PROXY_CONNECT_TIMEOUT,
        read=settings.PROXY_TIMEOUT,
        write=settings.PROXY_TIMEOUT,
        pool=settings.PROXY_TIMEOUT,
    )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            upstream = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )

            print("=" * 80)
            print("PRODUCT_SERVICE_URL:", settings.PRODUCT_SERVICE_URL)
            print("REQUEST PATH:", request.url.path)
            print("FINAL URL:", url)
            print("=" * 80)

    except httpx.ConnectError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Product service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Product service timed out.")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(upstream.headers),
        media_type=upstream.headers.get("content-type"),
    )


# ── Public (read-only) ────────────────────────────────────────────────────────

@router.get("")
@router.get("/")
async def list_products(request: Request, settings: Settings = Depends(get_settings)):
    """Browse the product catalogue (paginated, filterable)."""
    return await _proxy(request, settings)


@router.get("/search")
async def search_products(request: Request, settings: Settings = Depends(get_settings)):
    """Full-text product search."""
    return await _proxy(request, settings)


@router.get("/{product_id}")
async def get_product(request: Request, settings: Settings = Depends(get_settings)):
    """Retrieve a single product by ID."""
    return await _proxy(request, settings)


@router.get("/{product_id}/reviews")
async def get_reviews(request: Request, settings: Settings = Depends(get_settings)):
    """List reviews for a product."""
    return await _proxy(request, settings)


# ── Protected (admin/seller mutations) ───────────────────────────────────────

@router.post("")
@router.post("/")
async def create_product(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Create a new product listing."""
    return await _proxy(request, settings, payload)


@router.put("/{product_id}")
async def replace_product(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Replace a product (full update)."""
    return await _proxy(request, settings, payload)


@router.patch("/{product_id}")
async def update_product(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Partial-update a product."""
    return await _proxy(request, settings, payload)


@router.delete("/{product_id}")
async def delete_product(
    request: Request,
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Remove a product from the catalogue."""
    return await _proxy(request, settings)


@router.post("/{product_id}/reviews")
async def post_review(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Submit a review for a product."""
    return await _proxy(request, settings, payload)
