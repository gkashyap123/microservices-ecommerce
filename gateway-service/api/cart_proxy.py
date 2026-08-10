"""
Cart Proxy
Forwards /cart/* requests to the upstream cart-service.
All cart operations require authentication (carts are per-user).
"""
import httpx
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body

from api.proxy_utils import build_proxy_content, make_proxy_headers
from core.config import get_settings, Settings
from core.cors import get_cors_origins
from core.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


async def _proxy(request: Request, settings: Settings, payload: dict | None = None, path_override: str | None = None) -> Response:
    # Allow callers to override the proxied path (useful for injecting user id)
    if path_override is not None:
        url = f"{settings.CART_SERVICE_URL}{path_override}"
    else:
        url = f"{settings.CART_SERVICE_URL}{request.url.path}"
        if request.url.query:
            url = f"{url}?{request.url.query}"

    body = await build_proxy_content(request, payload)
    headers = make_proxy_headers(request, payload)

    timeout = httpx.Timeout(
        connect=settings.PROXY_CONNECT_TIMEOUT,
        read=settings.PROXY_TIMEOUT,
        write=settings.PROXY_TIMEOUT,
        pool=settings.PROXY_TIMEOUT,
    )

    try:
        client = request.app.state.http_client
        upstream = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )
    except httpx.ConnectError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Cart service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Cart service timed out.")
    except httpx.HTTPError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Cart proxy error: {exc}")

    # Ensure CORS headers are present on proxied responses so browser receives them
    response_headers = dict(upstream.headers)
    origin = request.headers.get("origin")
    allowed = get_cors_origins()
    if origin and origin in allowed:
        response_headers["access-control-allow-origin"] = origin
        response_headers["access-control-allow-credentials"] = "true"
    else:
        # fallback to first allowed origin or wildcard
        response_headers["access-control-allow-origin"] = allowed[0] if allowed else "*"

    # Allow common CORS request headers/methods in case browser inspects the response
    response_headers.setdefault("access-control-allow-methods", "GET,POST,PUT,DELETE,OPTIONS")
    response_headers.setdefault("access-control-allow-headers", "Authorization,Content-Type")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


# All routes are protected — a cart belongs to a user
_auth = Depends(get_current_user)


@router.get("", dependencies=[_auth])
@router.get("/", dependencies=[_auth])
async def get_cart(request: Request, settings: Settings = Depends(get_settings), current_user=Depends(get_current_user)):
    """Retrieve the authenticated user's cart."""
    user_id = current_user.get("sub")
    return await _proxy(request, settings, path_override=f"/cart/{user_id}")


@router.post("/items", dependencies=[_auth])
async def add_item(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings), current_user=Depends(get_current_user)):
    """Add an item (or increase quantity) in the cart."""
    user_id = current_user.get("sub")
    return await _proxy(request, settings, payload, path_override=f"/cart/{user_id}/items")


@router.put("/items/{item_id}", dependencies=[_auth])
async def update_item(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings), current_user=Depends(get_current_user)):
    """Update quantity for a specific cart item."""
    user_id = current_user.get("sub")
    item_id = request.path_params.get("item_id")
    return await _proxy(request, settings, payload=payload, path_override=f"/cart/{user_id}/items/{item_id}")


@router.delete("/items/{item_id}", dependencies=[_auth])
async def remove_item(request: Request, settings: Settings = Depends(get_settings), current_user=Depends(get_current_user)):
    """Remove a single item from the cart."""
    user_id = current_user.get("sub")
    item_id = request.path_params.get("item_id")
    return await _proxy(request, settings, path_override=f"/cart/{user_id}/items/{item_id}")


@router.delete("", dependencies=[_auth])
@router.delete("/", dependencies=[_auth])
async def clear_cart(request: Request, settings: Settings = Depends(get_settings), current_user=Depends(get_current_user)):
    """Empty the cart completely."""
    user_id = current_user.get("sub")
    return await _proxy(request, settings, path_override=f"/cart/{user_id}")


@router.post("/coupon", dependencies=[_auth])
async def apply_coupon(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Apply a coupon / promo code to the cart."""
    return await _proxy(request, settings, payload)


@router.delete("/coupon", dependencies=[_auth])
async def remove_coupon(request: Request, settings: Settings = Depends(get_settings)):
    """Remove the applied coupon from the cart."""
    return await _proxy(request, settings)
