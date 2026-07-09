from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6380
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    APP_NAME: str = "cart-service"
    CART_TTL_SECONDS: int = 86400       # 24 hours

    class Config:
        env_file = ".env"

settings = Settings()