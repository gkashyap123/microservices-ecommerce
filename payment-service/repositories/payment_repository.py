from sqlalchemy.orm import Session
from models.payment import Payment, PaymentStatus

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_by_razorpay_order_id(self, razorpay_order_id: str) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.razorpay_order_id == razorpay_order_id)
            .first()
        )

    def get_by_order_id(self, order_id: int) -> Payment | None:
        return self.db.query(Payment).filter(Payment.order_id == order_id).first()

    def get_by_user(
        self, user_id: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[Payment], int]:
        query = (
            self.db.query(Payment)
            .filter(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        total   = query.count()
        results = query.offset((page - 1) * page_size).limit(page_size).all()
        return results, total

    def create(
        self,
        order_id: int,
        user_id: str,
        amount: float,
        currency: str,
        razorpay_order_id: str,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            razorpay_order_id=razorpay_order_id,
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_success(
        self,
        payment: Payment,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Payment:
        payment.status              = PaymentStatus.SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature  = razorpay_signature
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_failed(self, payment: Payment) -> Payment:
        payment.status = PaymentStatus.FAILED
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_refunded(
        self,
        payment: Payment,
        refund_id: str,
        refunded_amount: float,
        reason: str,
    ) -> Payment:
        payment.refund_id       = refund_id
        payment.refunded_amount = refunded_amount
        payment.refund_reason   = reason
        payment.status          = (
            PaymentStatus.REFUNDED
            if refunded_amount >= payment.amount
            else PaymentStatus.PARTIAL_REFUND
        )
        self.db.commit()
        self.db.refresh(payment)
        return payment