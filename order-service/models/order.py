import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base

class OrderStatus(str, enum.Enum):
    PENDING   = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED   = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED    = "FAILED"

class Order(Base):
    __tablename__ = "orders"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(String, nullable=False, index=True)
    status      = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # One order → many order items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")