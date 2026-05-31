"""User repository."""

from typing import Optional
from sqlalchemy.orm import Session

from app.models import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

    def get_active_by_id(self, id: int) -> Optional[User]:
        """Get active user by ID."""
        return self.db.query(User).filter(
            User.id == id,
            User.is_active == True,
            User.is_deleted == False
        ).first()

    def get_all_active(self, skip: int = 0, limit: int = 100):
        """Get all active users."""
        return self.db.query(User).filter(
            User.is_active == True,
            User.is_deleted == False
        ).offset(skip).limit(limit).all()

    def create_user(self, email: str, password_hash: str, role: str) -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            self.db.refresh(user)
        return user
