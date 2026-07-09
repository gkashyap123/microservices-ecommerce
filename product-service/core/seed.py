from sqlalchemy.orm import Session
from models.category import Category
from models.product import Product


def seed_db(db: Session) -> None:
    """Insert initial categories and products if they don't exist."""
    # If categories already exist, assume DB is seeded
    existing = db.query(Category).count()
    if existing > 0:
        return

    # Create two categories
    cat1 = Category(name="Electronics", description="Electronic gadgets and devices")
    cat2 = Category(name="Home", description="Home and kitchen products")
    db.add_all([cat1, cat2])
    db.flush()  # assign IDs

    # Create five products across two categories
    products = [
        Product(name="Wireless Headphones", description="Noise-cancelling over-ear headphones", price=99.99, stock=50, category_id=cat1.id),
        Product(name="Smartphone", description="Latest model smartphone with OLED display", price=699.0, stock=30, category_id=cat1.id),
        Product(name="Bluetooth Speaker", description="Portable waterproof speaker", price=49.99, stock=100, category_id=cat1.id),
        Product(name="Ceramic Mug", description="350ml ceramic coffee mug", price=9.99, stock=200, category_id=cat2.id),
        Product(name="Kitchen Knife Set", description="Stainless steel 5-piece knife set", price=59.99, stock=80, category_id=cat2.id),
    ]

    db.add_all(products)
    db.commit()
