from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gateway
    APP_NAME: str = "API Gateway Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Upstream service base URLs

    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    PRODUCT_SERVICE_URL: str = "http://product-service:8000"
    CART_SERVICE_URL: str = "http://cart-service:8000"
    ORDER_SERVICE_URL: str = "http://order-service:8000"
    PAYMENT_SERVICE_URL: str = "http://payment-service:8000"

    # AUTH_SERVICE_URL: str = "http://localhost:8001"
    # PRODUCT_SERVICE_URL: str = "http://localhost:8002"
    # CART_SERVICE_URL: str = "http://localhost:8003"
    # ORDER_SERVICE_URL: str = "http://localhost:8004"
    # PAYMENT_SERVICE_URL: str = "http://localhost:8005"



    # Proxy timeouts (seconds)
    PROXY_TIMEOUT: int = 30
    PROXY_CONNECT_TIMEOUT: int = 10

    # JWT verification (shared secret — keep in sync with auth-service)
    JWT_SECRET_KEY: str = "7dF0qv6MZ8xN2kLp3Rb9Ws4Yt1Hg5JcU"
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS:  str #list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
