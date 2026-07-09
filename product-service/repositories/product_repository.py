from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from models.product import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        category_id: int | None = None,
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> tuple[list[Product], int]:

        query = self.db.query(Product).options(joinedload(Product.category))

        # --- Filters ---
        if category_id:
            query = query.filter(Product.category_id == category_id)

        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                )
            )

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        total = query.count()

        # --- Pagination ---
        products = query.offset((page - 1) * page_size).limit(page_size).all()

        return products, total

    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id)
            .first()
        )

    def create(self, data: dict) -> Product:
        product = Product(**data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return self.get_by_id(product.id)   # re-fetch with category joined

    def update(self, product: Product, data: dict) -> Product:
        for key, value in data.items():
            if value is not None:
                setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return self.get_by_id(product.id)

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()