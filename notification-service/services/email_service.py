import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from core.config import settings
from schemas.events import OrderEvent, OrderStatus
import os

# Load templates from app/templates/email/
template_env = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.dirname(__file__), "../templates/email")
    ),
    autoescape=select_autoescape(["html"])
)

# Map order status → template file + subject line
STATUS_CONFIG = {
    OrderStatus.CONFIRMED: {
        "template": "order_confirmed.html",
        "subject": "✅ Your Order #{order_id} is Confirmed!",
    },
    OrderStatus.SHIPPED: {
        "template": "order_shipped.html",
        "subject": "🚚 Your Order #{order_id} has been Shipped!",
    },
    OrderStatus.DELIVERED: {
        "template": "order_delivered.html",
        "subject": "📦 Your Order #{order_id} has been Delivered!",
    },
    OrderStatus.CANCELLED: {
        "template": "order_cancelled.html",
        "subject": "❌ Your Order #{order_id} has been Cancelled",
    },
    OrderStatus.FAILED: {
        "template": "order_failed.html",
        "subject": "⚠️ Your Order #{order_id} Failed",
    },
}

class EmailService:

    async def send(self, event: OrderEvent) -> None:
        config = STATUS_CONFIG.get(event.status)
        if not config:
            print(f"No email template for status: {event.status}")
            return

        # Render HTML template
        template = template_env.get_template(config["template"])
        html_body = template.render(
            order_id=event.order_id,
            user_id=event.user_id,
            items=event.items,
            total_price=event.total_price,
            failure_reason=event.failure_reason,
        )

        subject = config["subject"].format(order_id=event.order_id)

        # Build email
        message = MIMEMultipart("alternative")
        message["From"]    = settings.EMAIL_FROM
        message["To"]      = event.user_email
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        # Send via async SMTP
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            print(f"Email sent to {event.user_email} for order #{event.order_id} [{event.status}]")
        except Exception as e:
            print(f"Failed to send email for order #{event.order_id}: {e}")