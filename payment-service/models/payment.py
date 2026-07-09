import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Text, func
from core.database import Base

class PaymentStatus(str, enum.Enum):
    CREATED        = "CREATED"         # Razorpay order created, awaiting payment
    SUCCESS        = "SUCCESS"         # Payment verified and confirmed
    FAILED         = "FAILED"          # Payment failed or bad signature
    REFUNDED       = "REFUNDED"        # Full refund processed
    PARTIAL_REFUND = "PARTIAL_REFUND"  # Partial refund processed

class Payment(Base):
    __tablename__ = "payments"

    id                  = Column(Integer, primary_key=True, index=True)
    order_id            = Column(Integer, nullable=False, index=True)
    user_id             = Column(String, nullable=False, index=True)
    amount              = Column(Float, nullable=False)
    currency            = Column(String(10), default="INR")
    status              = Column(Enum(PaymentStatus), default=PaymentStatus.CREATED)

    # Razorpay fields
    razorpay_order_id   = Column(String, unique=True, nullable=False, index=True)
    razorpay_payment_id = Column(String, unique=True, nullable=True)
    razorpay_signature  = Column(String, nullable=True)

    # Refund fields
    refund_id           = Column(String, nullable=True)
    refunded_amount     = Column(Float, nullable=True)
    refund_reason       = Column(Text, nullable=True)

    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())