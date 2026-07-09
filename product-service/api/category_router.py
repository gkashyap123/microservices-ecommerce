from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=list[CategoryResponse])
def get_all(db: Session = Depends(get_db)):
    return CategoryService(db).get_all()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_one(category_id: int, db: Session = Depends(get_db)):
    return CategoryService(db).get_by_id(category_id)

@router.post("/", response_model=CategoryResponse, status_code=201)
def create(payload: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService(db).create(payload)

@router.put("/{category_id}", response_model=CategoryResponse)
def update(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    return CategoryService(db).update(category_id, payload)

@router.delete("/{category_id}")
def delete(category_id: int, db: Session = Depends(get_db)):
    return CategoryService(db).delete(category_id)