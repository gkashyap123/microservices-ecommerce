from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "notification-service"

    # RabbitMQ
    RABBITMQ_URL: str
    QUEUE_NAME: str = "order_events"

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str

    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str

    class Config:
        env_file = ".env"

settings = Settings()