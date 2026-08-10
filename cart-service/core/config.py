from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379"
    APP_NAME: str = "cart-service"
    CART_TTL_SECONDS: int = 86400       # 24 hours

    class Config:
        env_file = ".env"

settings = Settings()