"""
Auth Proxy
Forwards all /auth/* requests to the upstream auth-service.
Public routes: /auth/login, /auth/register, /auth/refresh
Protected routes: everything else (requires valid JWT)
"""
import httpx
import json
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse

from core.config import get_settings, Settings
from core.cors import get_cors_origins
from core.dependencies import get_current_user   # shared JWT guard

router = APIRouter(prefix="/auth", tags=["Auth"])

# These paths do NOT require an existing token
_PUBLIC_PATHS = {"/auth/login", "/auth/register", "/auth/refresh"}


async def _proxy(
    request: Request,
    settings: Settings,
    strip_prefix: str = "",
    payload: dict | None = None,
) -> Response:
    """Forward the incoming request to the auth-service and stream the response back."""
    target_path = request.url.path
    if strip_prefix:
        target_path = target_path.removeprefix(strip_prefix)

    url = f"{settings.AUTH_SERVICE_URL}{target_path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    else:
        body = await request.body()

    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    if payload is not None and "content-type" not in {k.lower() for k in headers.keys()}:
        headers["content-type"] = "application/json"
        
    #headers = dict(request.headers)
    #headers.pop("host", None)

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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service is unreachable.",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Auth service timed out.",
        )

    response_headers = dict(upstream.headers)
    origin = request.headers.get("origin")
    allowed = get_cors_origins()
    if origin and origin in allowed:
        response_headers["access-control-allow-origin"] = origin
        response_headers["access-control-allow-credentials"] = "true"
    else:
        response_headers.setdefault("access-control-allow-origin", allowed[0] if allowed else "*")
        response_headers.setdefault("access-control-allow-credentials", "true")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.post("/login")
async def login(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Obtain access + refresh tokens."""
    return await _proxy(request, settings, payload=payload)


@router.post("/register")
async def register(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Create a new user account."""
    return await _proxy(request, settings, payload=payload)


@router.post("/refresh")
async def refresh_token(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Exchange a refresh token for a new access token."""
    return await _proxy(request, settings, payload=payload)


# ── Protected endpoints ───────────────────────────────────────────────────────

@router.get("/me")
async def get_profile(
    request: Request,
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    return await _proxy(request, settings)


@router.put("/me")
async def update_profile(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Update the authenticated user's profile."""
    return await _proxy(request, settings, payload=payload)


@router.post("/logout")
async def logout(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Invalidate the current session / refresh token."""
    return await _proxy(request, settings, payload=payload)


@router.post("/change-password")
async def change_password(
    request: Request,
    payload: dict | None = Body(None),
    settings: Settings = Depends(get_settings),
    _user=Depends(get_current_user),
):
    """Change the authenticated user's password."""
    return await _proxy(request, settings, payload=payload)
