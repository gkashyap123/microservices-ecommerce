"""
Order Proxy
Forwards /orders/* requests to the upstream order-service.
All order operations require authentication.
Admin-only routes (cancel any order, list all orders) can be further
restricted inside the order-service using the forwarded JWT claims.
"""
import httpx
import json
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body

from core.config import get_settings, Settings
from core.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


async def _proxy(request: Request, settings: Settings, payload: dict | None = None) -> Response:
    url = f"{settings.ORDER_SERVICE_URL}{request.url.path}"
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
    except httpx.ConnectError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Order service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Order service timed out.")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(upstream.headers),
        media_type=upstream.headers.get("content-type"),
    )


_auth = Depends(get_current_user)


@router.get("", dependencies=[_auth])
@router.get("/", dependencies=[_auth])
async def list_orders(request: Request, settings: Settings = Depends(get_settings)):
    """List the authenticated user's orders (admins see all)."""
    return await _proxy(request, settings)


@router.post("", dependencies=[_auth])
@router.post("/", dependencies=[_auth])
async def place_order(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Place a new order from the current cart."""
    return await _proxy(request, settings, payload)


@router.get("/{order_id}", dependencies=[_auth])
async def get_order(request: Request, settings: Settings = Depends(get_settings)):
    """Retrieve a single order by ID."""
    return await _proxy(request, settings)


@router.post("/{order_id}/cancel", dependencies=[_auth])
async def cancel_order(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Request cancellation of an order."""
    return await _proxy(request, settings, payload)


@router.get("/{order_id}/tracking", dependencies=[_auth])
async def track_order(request: Request, settings: Settings = Depends(get_settings)):
    """Get shipment tracking info for an order."""
    return await _proxy(request, settings)


@router.post("/{order_id}/return", dependencies=[_auth])
async def return_order(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Initiate a return / refund request for an order."""
    return await _proxy(request, settings, payload)
