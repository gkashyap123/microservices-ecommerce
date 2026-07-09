from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    name       = Column(String(200), nullable=False)   # snapshot at order time
    price      = Column(Float, nullable=False)          # snapshot at order time
    quantity   = Column(Integer, nullable=False)
    subtotal   = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")