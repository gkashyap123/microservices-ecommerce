import json
import asyncio
import aio_pika
from core.config import settings
from schemas.events import OrderEvent
from services.email_service import EmailService
from services.sms_service import SmsService

email_service = EmailService()
sms_service   = SmsService()

async def process_event(message: aio_pika.IncomingMessage) -> None:
    """Called for every message received from RabbitMQ."""
    async with message.process():     # auto ack on success, nack on exception
        try:
            # Deserialize event
            body = json.loads(message.body.decode())
            event = OrderEvent(**body)

            print(f"Processing event: {event.event_type} | Order #{event.order_id}")

            # Send Email + SMS concurrently
            await asyncio.gather(
                email_service.send(event),
                sms_service.send(event),
            )

            print(f"Notifications sent for order #{event.order_id} [{event.status}]")

        except Exception as e:
            print(f"Error processing message: {e}")
            raise   # triggers nack → message goes back to queue


async def start_consumer() -> None:
    """Connects to RabbitMQ and starts consuming order events."""
    print(f"Connecting to RabbitMQ at {settings.RABBITMQ_URL}...")

    # Retry loop — wait for RabbitMQ to be ready
    while True:
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            break
        except Exception as e:
            print(f"RabbitMQ not ready, retrying in 3s... ({e})")
            await asyncio.sleep(3)

    channel = await connection.channel()

    # Fair dispatch — don't push more than 1 unacked message per consumer
    await channel.set_qos(prefetch_count=1)

    # Declare queue (creates it if it doesn't exist)
    queue = await channel.declare_queue(
        settings.QUEUE_NAME,
        durable=True      # survives RabbitMQ restart
    )

    print(f"Listening on queue: '{settings.QUEUE_NAME}'")
    await queue.consume(process_event)

    # Keep consumer alive forever
    await asyncio.Future()