from twilio.rest import Client
from core.config import settings
from schemas.events import OrderEvent, OrderStatus

# SMS message templates per status
SMS_TEMPLATES = {
    OrderStatus.CONFIRMED: (
        "✅ Order #{order_id} confirmed! "
        "Total: ${total_price}. "
        "We'll notify you when it ships."
    ),
    OrderStatus.SHIPPED: (
        "🚚 Order #{order_id} is on its way! "
        "Expected delivery in 2-3 business days."
    ),
    OrderStatus.DELIVERED: (
        "📦 Order #{order_id} delivered! "
        "Thank you for shopping with us."
    ),
    OrderStatus.CANCELLED: (
        "❌ Order #{order_id} has been cancelled. "
        "Refund will be processed in 3-5 business days."
    ),
    OrderStatus.FAILED: (
        "⚠️ Order #{order_id} failed. "
        "Reason: {failure_reason}. Please try again."
    ),
}

class SmsService:

    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    async def send(self, event: OrderEvent) -> None:
        template = SMS_TEMPLATES.get(event.status)
        if not template:
            print(f"No SMS template for status: {event.status}")
            return

        message_body = template.format(
            order_id=event.order_id,
            total_price=event.total_price,
            failure_reason=event.failure_reason or "Unknown error",
        )

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=settings.TWILIO_FROM_NUMBER,
                to=event.user_phone,
            )
            print(f"SMS sent to {event.user_phone} for order #{event.order_id} "
                  f"[{event.status}] SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS for order #{event.order_id}: {e}")