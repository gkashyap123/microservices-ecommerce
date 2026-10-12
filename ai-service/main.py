from fastapi import FastAPI

from api.chat import router as chat_router
from api.rag import router as rag_router



app = FastAPI(
    title="AI Service",
    description="GenAI service for e-commerce platform",
    version="1.0.0",
)

app.include_router(rag_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ai-service",
    }


@app.get("/")
async def root():
    return {
        "message": "AI Service is running"
    }