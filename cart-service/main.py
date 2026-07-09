from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.redis import redis_client
from core.cors import get_cors_origins
from api.cart_router import router
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify Redis connection on startup
    redis_client.ping()
    print("Redis connected successfully")
    yield
    redis_client.close()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health():
    redis_ok = redis_client.ping()
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "redis": "connected" if redis_ok else "disconnected"
    }