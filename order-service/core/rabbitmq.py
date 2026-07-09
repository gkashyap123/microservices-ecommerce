import json
import aio_pika
from core.config import settings

# In place_order(), after CONFIRMED

async def publish_order_event(event: dict) -> None:
    """Publishes an order event to RabbitMQ."""
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            # Declare same queue (idempotent)
            await channel.declare_queue("order_events", durable=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(event).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # survive restart
                ),
                routing_key="order_events",
            )
            print(f"Published event: {event.get('event_type')}")
    except Exception as e:
        print(f"Failed to publish event: {e}")   # don't crash order for notification failure