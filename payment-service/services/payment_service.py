import json
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from services.razorpay_service import RazorpayService
from clients.order_client import OrderClient
from repositories.payment_repository import PaymentRepository
from core.rabbitmq import publish_payment_event
from core.config import settings
from schemas.payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    VerifyPaymentRequest,
    RefundRequest,
)

class PaymentService:
    def __init__(self, db: Session):
        self.repo         = PaymentRepository(db)
        self.razorpay     = RazorpayService()
        self.order_client = OrderClient()

    # ── Create ────────────────────────────────────────────────────────

    async def create_payment(self, payload: CreatePaymentRequest) -> CreatePaymentResponse:

        # Prevent duplicate payment for same order
        if self.repo.get_by_order_id(payload.order_id):
            raise HTTPException(
                status_code=400,
                detail=f"Payment already exists for order #{payload.order_id}"
            )

        # Create Razorpay order
        receipt  = f"order_{payload.order_id}_user_{payload.user_id}"
        rz_order = self.razorpay.create_order(
            payload.amount, payload.currency, receipt
        )

        # Save to DB (status = CREATED)
        payment = self.repo.create(
            order_id=payload.order_id,
            user_id=payload.user_id,
            amount=payload.amount,
            currency=payload.currency,
            razorpay_order_id=rz_order["id"],
        )

        return CreatePaymentResponse(
            payment_id=payment.id,
            razorpay_order_id=rz_order["id"],
            razorpay_key_id=settings.RAZORPAY_KEY_ID,   # frontend needs this
            amount=payload.amount,
            currency=payload.currency,
        )

    # ── Verify ────────────────────────────────────────────────────────

    async def verify_payment(self, payload: VerifyPaymentRequest):

        payment = self.repo.get_by_razorpay_order_id(payload.razorpay_order_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment record not found")

        # Security — verify HMAC signature before doing anything
        is_valid = self.razorpay.verify_signature(
            payload.razorpay_order_id,
            payload.razorpay_payment_id,
            payload.razorpay_signature,
        )

        if not is_valid:
            self.repo.mark_failed(payment)
            await publish_payment_event({
                "event_type": "payment.failed",
                "payment_id": payment.id,
                "order_id":   payment.order_id,
                "user_id":    payment.user_id,
                "amount":     payment.amount,
                "reason":     "Invalid signature",
            })
            raise HTTPException(
                status_code=400,
                detail="Invalid payment signature — possible tampering detected"
            )

        # Mark SUCCESS in DB
        payment = self.repo.mark_success(
            payment,
            payload.razorpay_payment_id,
            payload.razorpay_signature,
        )

        # Update order-service → CONFIRMED
        await self.order_client.update_order_status(payment.order_id, "CONFIRMED")

        # Publish success event
        await publish_payment_event({
            "event_type":          "payment.success",
            "payment_id":          payment.id,
            "order_id":            payment.order_id,
            "user_id":             payment.user_id,
            "amount":              payment.amount,
            "currency":            payment.currency,
            "razorpay_payment_id": payment.razorpay_payment_id,
            "razorpay_order_id":   payment.razorpay_order_id,
        })

        return payment

    # ── Webhook ───────────────────────────────────────────────────────

    async def handle_webhook(self, request: Request):
        body      = await request.body()
        signature = request.headers.get("X-Razorpay-Signature", "")

        if not self.razorpay.verify_webhook_signature(body, signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        event_data = json.loads(body)
        event_type = event_data.get("event")
        print(f"Razorpay webhook received: {event_type}")

        # Handle payment.failed webhook
        if event_type == "payment.failed":
            rz_order_id = (
                event_data
                .get("payload", {})
                .get("payment", {})
                .get("entity", {})
                .get("order_id")
            )
            if rz_order_id:
                payment = self.repo.get_by_razorpay_order_id(rz_order_id)
                if payment:
                    self.repo.mark_failed(payment)
                    await self.order_client.update_order_status(
                        payment.order_id, "FAILED"
                    )
                    await publish_payment_event({
                        "event_type": "payment.failed",
                        "payment_id": payment.id,
                        "order_id":   payment.order_id,
                        "user_id":    payment.user_id,
                        "amount":     payment.amount,
                    })

        return {"status": "webhook processed"}

    # ── Refund ────────────────────────────────────────────────────────

    async def process_refund(self, payload: RefundRequest):
        payment = self.repo.get_by_id(payload.payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status != "SUCCESS":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot refund a payment with status '{payment.status}'"
            )

        if not payment.razorpay_payment_id:
            raise HTTPException(
                status_code=400,
                detail="No Razorpay payment ID found — cannot process refund"
            )

        # Validate refund amount
        refund_amount = payload.amount or payment.amount
        if refund_amount > payment.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Refund ₹{refund_amount} exceeds paid amount ₹{payment.amount}"
            )

        # Process via Razorpay
        refund = self.razorpay.process_refund(
            payment.razorpay_payment_id, payload.amount
        )

        # Update DB
        payment = self.repo.mark_refunded(
            payment,
            refund_id=refund["id"],
            refunded_amount=refund_amount,
            reason=payload.reason,
        )

        # Publish refund event
        await publish_payment_event({
            "event_type":      "payment.refunded",
            "payment_id":      payment.id,
            "order_id":        payment.order_id,
            "user_id":         payment.user_id,
            "refund_id":       refund["id"],
            "refunded_amount": refund_amount,
            "reason":          payload.reason,
        })

        return payment

    # ── Read ──────────────────────────────────────────────────────────

    def get_by_id(self, payment_id: int):
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    def get_by_order(self, order_id: int):
        payment = self.repo.get_by_order_id(order_id)
        if not payment:
            raise HTTPException(
                status_code=404,
                detail=f"No payment found for order #{order_id}"
            )
        return payment

    def get_user_payments(self, user_id: str, page: int, page_size: int):
        payments, total = self.repo.get_by_user(user_id, page, page_size)
        return {
            "total":     total,
            "page":      page,
            "page_size": page_size,
            "results":   payments,
        }