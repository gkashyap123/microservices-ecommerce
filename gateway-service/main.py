"""
API Gateway — main entrypoint
Assembles all proxy routers, middleware, and startup/shutdown hooks.
"""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.cors import get_cors_origins
from api.auth_proxy import router as auth_router
from api.product_proxy import router as product_router
from api.cart_proxy import router as cart_router
from api.order_proxy import router as order_router
from api.payment_proxy import router as payment_router
from api.category_proxy import router as category_router

settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic (e.g. warm-up shared HTTP client pools)."""
    print(f"🚀  {settings.APP_NAME} v{settings.APP_VERSION} starting …")
    timeout = httpx.Timeout(
        connect=settings.PROXY_CONNECT_TIMEOUT,
        read=settings.PROXY_TIMEOUT,
        write=settings.PROXY_TIMEOUT,
        pool=settings.PROXY_TIMEOUT,
    )
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.http_client = client
        yield
    print("🛑  Gateway shutting down.")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Central API Gateway that routes and authenticates requests "
        "for Auth, Product, Cart, Order, and Payment micro-services."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers ─────────────────────────────────────────────────

@app.exception_handler(httpx.ConnectError)
async def connect_error_handler(request: Request, exc: httpx.ConnectError):
    return JSONResponse(
        status_code=503,
        content={"detail": "An upstream service is currently unavailable."},
    )

@app.exception_handler(httpx.HTTPError)
async def httpx_error_handler(request: Request, exc: httpx.HTTPError):
    return JSONResponse(
        status_code=502,
        content={"detail": "Upstream request failed.", "error": str(exc)},
    )

@app.options("/{full_path:path}")
async def preflight(full_path: str, request: Request):
    return Response(status_code=204)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(category_router)

# ── Health & meta endpoints ───────────────────────────────────────────────────

@app.get("/health", tags=["Gateway"], summary="Gateway health check")
async def health():
    """Returns 200 when the gateway process is alive."""
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health/upstream", tags=["Gateway"], summary="Upstream service health check")
async def upstream_health():
    """
    Pings each upstream service's /health endpoint and aggregates results.
    Useful for readiness probes and dashboards.
    """
    services = {
        "auth":    f"{settings.AUTH_SERVICE_URL}/health",
        "product": f"{settings.PRODUCT_SERVICE_URL}/health",
        "cart":    f"{settings.CART_SERVICE_URL}/health",
        "order":   f"{settings.ORDER_SERVICE_URL}/health",
        "payment": f"{settings.PAYMENT_SERVICE_URL}/health",
    }

    results = {}
    timeout = httpx.Timeout(connect=3, read=5, write=5, pool=5)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for name, url in services.items():
            try:
                r = await client.get(url)
                results[name] = {"status": "ok" if r.status_code == 200 else "degraded", "code": r.status_code}
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                results[name] = {"status": "unreachable", "error": str(exc)}

    overall = "ok" if all(v["status"] == "ok" for v in results.values()) else "degraded"
    return {"overall": overall, "services": results}


@app.get("/", tags=["Gateway"], include_in_schema=False)
async def root():
    return {
        "gateway": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
