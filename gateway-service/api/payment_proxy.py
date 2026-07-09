"""
Payment Proxy
Forwards /payments/* requests to the upstream payment-service.

IMPORTANT: The webhook endpoint (/payments/webhook) is intentionally
PUBLIC — payment providers (Razorpay, Stripe, etc.) call it directly
with their own HMAC signature. Signature verification happens inside
the payment-service itself.
"""
import httpx
import json
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body

from core.config import get_settings, Settings
from core.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


async def _proxy(request: Request, settings: Settings, payload: dict | None = None) -> Response:
    url = f"{settings.PAYMENT_SERVICE_URL}{request.url.path}"
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
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Payment service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Payment service timed out.")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(upstream.headers),
        media_type=upstream.headers.get("content-type"),
    )


_auth = Depends(get_current_user)


# ── Protected ─────────────────────────────────────────────────────────────────

@router.post("/initiate", dependencies=[_auth])
async def initiate_payment(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Create a payment intent / order with the payment gateway."""
    return await _proxy(request, settings, payload)


@router.get("/{payment_id}", dependencies=[_auth])
async def get_payment(request: Request, settings: Settings = Depends(get_settings)):
    """Retrieve the status of a payment."""
    return await _proxy(request, settings)


@router.post("/{payment_id}/verify", dependencies=[_auth])
async def verify_payment(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Verify a completed payment signature client-side."""
    return await _proxy(request, settings, payload)


@router.post("/{payment_id}/refund", dependencies=[_auth])
async def refund_payment(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Initiate a refund for a completed payment."""
    return await _proxy(request, settings, payload)


@router.get("", dependencies=[_auth])
@router.get("/", dependencies=[_auth])
async def list_payments(request: Request, settings: Settings = Depends(get_settings)):
    """List payments for the authenticated user."""
    return await _proxy(request, settings)


# ── Public — provider webhook (no JWT required) ───────────────────────────────

@router.post("/webhook")
async def payment_webhook(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """
    Receive payment-provider webhook events (Razorpay / Stripe / etc.).
    Signature verification is delegated to the payment-service.
    """
    return await _proxy(request, settings, payload)
