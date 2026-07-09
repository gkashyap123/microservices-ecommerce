from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository
from schemas.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)
        self.cat_repo = CategoryRepository(db)

    def get_all(self, page, page_size, category_id, search, min_price, max_price):
        products, total = self.repo.get_all(
            page, page_size, category_id, search, min_price, max_price
        )
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": products,
        }

    def get_by_id(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def create(self, payload: ProductCreate):
        # Validate category exists
        if not self.cat_repo.get_by_id(payload.category_id):
            raise HTTPException(status_code=404, detail="Category not found")
        return self.repo.create(payload.model_dump())

    def update(self, product_id: int, payload: ProductUpdate):
        product = self.get_by_id(product_id)
        if payload.category_id and not self.cat_repo.get_by_id(payload.category_id):
            raise HTTPException(status_code=404, detail="Category not found")
        return self.repo.update(product, payload.model_dump(exclude_none=True))

    def delete(self, product_id: int):
        product = self.get_by_id(product_id)
        self.repo.delete(product)
        return {"message": "Product deleted successfully"}