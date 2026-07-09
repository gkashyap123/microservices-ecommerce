from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "order-service"

    # External service URLs
    CART_SERVICE_URL: str = "http://localhost:8002"
    PRODUCT_SERVICE_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"

settings = Settings()