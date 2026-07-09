from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, category_id: int):
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def create(self, payload: CategoryCreate):
        if self.repo.get_by_name(payload.name):
            raise HTTPException(status_code=400, detail="Category name already exists")
        return self.repo.create(payload.name, payload.description)

    def update(self, category_id: int, payload: CategoryUpdate):
        category = self.get_by_id(category_id)
        return self.repo.update(category, payload.model_dump(exclude_none=True))

    def delete(self, category_id: int):
        category = self.get_by_id(category_id)
        if category.products:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category with existing products"
            )
        self.repo.delete(category)
        return {"message": "Category deleted successfully"}