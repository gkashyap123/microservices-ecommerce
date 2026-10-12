from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@order-db:5432/orderdb"
    APP_NAME: str = "order-service"

    # External service URLs
    CART_SERVICE_URL: str = "http://cart-service:8000"
    PRODUCT_SERVICE_URL: str = "http://product-service:8000"

    class Config:
        env_file = ".env"

settings = Settings()