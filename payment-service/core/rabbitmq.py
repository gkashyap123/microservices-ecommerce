import json
import aio_pika
from core.config import settings

async def publish_payment_event(event: dict) -> None:
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(settings.QUEUE_NAME, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(event).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.QUEUE_NAME,
            )
            print(f"Published: {event.get('event_type')}")
    except Exception as e:
        # Never crash payment flow for a notification failure
        print(f"RabbitMQ publish failed: {e}")