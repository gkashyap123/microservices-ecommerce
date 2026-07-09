from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    VerifyPaymentRequest,
    RefundRequest,
    PaymentResponse,
    PaymentListResponse,
)
from services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create", response_model=CreatePaymentResponse, status_code=201)
async def create_payment(
    payload: CreatePaymentRequest,
    db: Session = Depends(get_db),
):
    """Step 1 — Initiate. Returns razorpay_order_id for frontend checkout."""
    return await PaymentService(db).create_payment(payload)


@router.post("/verify", response_model=PaymentResponse)
async def verify_payment(
    payload: VerifyPaymentRequest,
    db: Session = Depends(get_db),
):
    """Step 2 — Verify signature after frontend completes payment."""
    return await PaymentService(db).verify_payment(payload)


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """Razorpay webhook — register this URL in Razorpay dashboard."""
    return await PaymentService(db).handle_webhook(request)


@router.post("/refund", response_model=PaymentResponse)
async def refund_payment(
    payload: RefundRequest,
    db: Session = Depends(get_db),
):
    """Full or partial refund for a successful payment."""
    return await PaymentService(db).process_refund(payload)


@router.get("/user/{user_id}", response_model=PaymentListResponse)
def get_user_payments(
    user_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Paginated payment history for a user."""
    return PaymentService(db).get_user_payments(user_id, page, page_size)


@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_by_order(order_id: int, db: Session = Depends(get_db)):
    """Get payment record by order ID."""
    return PaymentService(db).get_by_order(order_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get payment record by internal payment ID."""
    return PaymentService(db).get_by_id(payment_id)