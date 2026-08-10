"""
Category Proxy
Forwards /categories/* requests to the product-service.
"""
import httpx
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Body

from api.proxy_utils import build_proxy_content, make_proxy_headers
from core.config import get_settings, Settings
from core.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


async def _proxy(request: Request, settings: Settings, payload: dict | None = None) -> Response:
    url = f"{settings.PRODUCT_SERVICE_URL}{request.url.path}"
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
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Product service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Product service timed out.")
    except httpx.HTTPError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Product proxy error: {exc}")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(upstream.headers),
        media_type=upstream.headers.get("content-type"),
    )


# Public
@router.get("")
@router.get("/")
async def list_categories(request: Request, settings: Settings = Depends(get_settings)):
    """List all categories."""
    return await _proxy(request, settings)


@router.get("/{category_id}")
async def get_category(request: Request, settings: Settings = Depends(get_settings)):
    """Retrieve a single category by ID."""
    return await _proxy(request, settings)


# Protected (admin)
@router.post("", dependencies=[Depends(get_current_user)])
async def create_category(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Create a new category."""
    return await _proxy(request, settings, payload)


@router.put("/{category_id}", dependencies=[Depends(get_current_user)])
async def update_category(request: Request, payload: dict | None = Body(None), settings: Settings = Depends(get_settings)):
    """Update a category."""
    return await _proxy(request, settings, payload)


@router.delete("/{category_id}", dependencies=[Depends(get_current_user)])
async def delete_category(request: Request, settings: Settings = Depends(get_settings)):
    """Delete a category."""
    return await _proxy(request, settings)
