from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.payment import PaymentStatus

# ── Requests ──────────────────────────────────────────────────────────

class CreatePaymentRequest(BaseModel):
    order_id: int
    user_id: str
    amount: float = Field(gt=0, description="Amount in INR")
    currency: str = "INR"
    user_email: str
    user_phone: str

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class RefundRequest(BaseModel):
    payment_id: int
    amount: Optional[float] = None      # None = full refund
    reason: str = "requested_by_customer"

# ── Responses ─────────────────────────────────────────────────────────

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: str
    amount: float
    currency: str
    status: PaymentStatus
    razorpay_order_id: str
    razorpay_payment_id: Optional[str]
    refund_id: Optional[str]
    refunded_amount: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class CreatePaymentResponse(BaseModel):
    payment_id: int
    razorpay_order_id: str      # frontend passes this to Razorpay SDK
    razorpay_key_id: str        # frontend uses this to init Razorpay checkout
    amount: float
    currency: str

class PaymentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[PaymentResponse]