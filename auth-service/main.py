from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth_router import router
from core.cors import get_cors_origins
from core.database import Base, engine, wait_for_db

wait_for_db()
Base.metadata.create_all(bind=engine)   # creates tables on startup

app = FastAPI(title="Auth Service")

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
    return {"status": "ok"}