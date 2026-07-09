"""CORS configuration helper for all services"""
from typing import List
import os

def get_cors_origins() -> List[str]:
    """Get CORS origins from environment or use defaults"""
    cors_env = os.getenv("CORS_ORIGINS", "")
    
    if cors_env:
        # Support comma-separated origins
        return [origin.strip() for origin in cors_env.split(",")]
    
    # Default origins for development
    return [
        "http://localhost:3000",      # Next.js dev server
        "http://localhost:5173",      # Vite dev server
        "http://frontend:3000",       # Docker container
    ]
