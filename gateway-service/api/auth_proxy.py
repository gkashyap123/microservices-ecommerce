"""
Auth Proxy
Forwards all /auth/* requests to the upstream auth-service.
Public routes: /auth/login, /auth/register, /auth/refresh
Protected routes: everything else (requires valid JWT)
"""
import httpx
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body

from api.proxy_utils import build_proxy_content, make_proxy_headers
from core.config import get_settings, Settings
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

        print("=" * 80)
        print("AUTH_SERVICE_URL:", settings.AUTH_SERVICE_URL)
        print("REQUEST PATH:", request.url.path)
        print("FINAL URL:", url)
        print("=" * 80)

    except httpx.ConnectError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Auth service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Auth service timed out.")
    except httpx.HTTPError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Auth proxy error: {exc}")
    except httpx.HTTPError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Auth proxy error: {exc}")

    # Filter out hop-by-hop headers that should not be forwarded to the client.
    excluded = {
        "content-encoding",
        "transfer-encoding",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "upgrade",
    }
    response_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in excluded}

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
