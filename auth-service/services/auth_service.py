from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from core.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, username: str, email: str, password: str):
        if self.repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = hash_password(password)
        return self.repo.create(username, email, hashed)

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        return create_access_token({"sub": str(user.id)})