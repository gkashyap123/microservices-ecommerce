from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "payment-service"

    # Razorpay
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str

    # Other services
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    RABBITMQ_URL: str
    QUEUE_NAME: str = "payment_events"

    class Config:
        env_file = ".env"

settings = Settings()