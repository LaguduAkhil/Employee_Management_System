"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserLogin, UserCreate, TokenResponse
from app.utils.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Returns JWT access token and user information.
    """
    user_service = UserService(db)
    
    user = user_service.authenticate_user(user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token_response = user_service.create_token(user)
    return token_response


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    User registration endpoint.
    
    Creates new user account and returns JWT token.
    """
    user_service = UserService(db)
    
    try:
        user = user_service.register_user(user_create)
        token_response = user_service.create_token(user)
        return token_response
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user information.
    
    Requires valid JWT token in Authorization header.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout endpoint.
    
    Client should discard the JWT token.
    """
    return {"message": "Successfully logged out"}
