from contextlib import asynccontextmanager
import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine, SessionLocal
from core.cors import get_cors_origins
from api.category_router import router as category_router
from api.product_router import router as product_router
from core.seed import seed_db


def wait_for_db(timeout: int = 30, interval: float = 1.0) -> None:
    deadline = time.time() + timeout
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError:
            if time.time() > deadline:
                raise
            time.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed initial data if DB empty
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

    yield

app = FastAPI(title="Product Service", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category_router)
app.include_router(product_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}