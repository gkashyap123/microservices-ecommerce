import hmac
import hashlib
import razorpay
from fastapi import HTTPException
from core.config import settings

class RazorpayService:

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_order(self, amount: float, currency: str, receipt: str) -> dict:
        """Creates Razorpay order. Amount converted to paise (×100)."""
        try:
            return self.client.order.create({
                "amount":          int(amount * 100),
                "currency":        currency,
                "receipt":         receipt,
                "payment_capture": 1,           # auto-capture on success
            })
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Razorpay order creation failed: {str(e)}"
            )

    def verify_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """
        Verifies HMAC-SHA256 payment signature.
        Formula: HMAC(razorpay_order_id + | + razorpay_payment_id, secret)
        """
        body     = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, razorpay_signature)

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verifies Razorpay webhook signature using webhook secret."""
        expected = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def process_refund(
        self,
        razorpay_payment_id: str,
        amount: float | None = None,
    ) -> dict:
        """Initiates refund. Amount=None means full refund."""
        try:
            payload = {}
            if amount:
                payload["amount"] = int(amount * 100)   # to paise
            return self.client.payment.refund(razorpay_payment_id, payload)
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Razorpay refund failed: {str(e)}"
            )