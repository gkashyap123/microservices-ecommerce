from sqlalchemy.orm import Session
from models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, username: str, email: str, hashed_password: str) -> User:
        user = User(username=username, email=email, password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user