"""User service for authentication and user management."""

from typing import Optional
from sqlalchemy.orm import Session

from app.models import User
from app.repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, TokenResponse, UserResponse
from app.utils.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from datetime import timedelta


class UserService:
    """Service layer for user operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_create: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            user_create: User creation request
        
        Returns:
            Created user
        
        Raises:
            UserAlreadyExistsError: If email already exists
        """
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise UserAlreadyExistsError(f"Email {user_create.email} already registered")
        
        hashed_password = hash_password(user_create.password)
        user = self.user_repo.create_user(
            email=user_create.email,
            password_hash=hashed_password,
            role=user_create.role
        )
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password (plain text)
        
        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user

    def create_token(self, user: User) -> TokenResponse:
        """
        Create JWT token for user.
        
        Args:
            user: Authenticated user
        
        Returns:
            Token response with access token and user info
        """
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            expires_in=int(access_token_expires.total_seconds()),
            user=UserResponse.from_orm(user)
        )

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_active_by_id(user_id)

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account."""
        return self.user_repo.deactivate(user_id)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            True if successful, False otherwise
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(old_password, user.password_hash):
            return False
        
        user.password_hash = hash_password(new_password)
        self.db.commit()
        return True
