import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from consumers.order_consumer import start_consumer
from core.cors import get_cors_origins
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start RabbitMQ consumer as background task
    consumer_task = asyncio.create_task(start_consumer())
    print("Order event consumer started")
    yield
    # Graceful shutdown
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("Consumer stopped")

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}