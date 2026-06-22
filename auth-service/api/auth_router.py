from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from services.auth_service import AuthService
from dependencies.auth_dependency import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(payload.username, payload.email, payload.password)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login(payload.email, payload.password)
    return {"access_token": token}

@router.get("/me", response_model=UserResponse)
def me(current_user = Depends(get_current_user)):
    return current_user