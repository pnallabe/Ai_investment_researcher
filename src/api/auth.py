"""
Authentication and authorization for the AI Investment Research Bot API.

Implements JWT-based authentication with role-based access control.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import logging

from config.settings import Settings
from src.models.postgresql import User, UserRole

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT security
security = HTTPBearer()

# Router
auth_router = APIRouter()


class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.ANALYST


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    role: str


class TokenData(BaseModel):
    """JWT token data model."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class AuthService:
    """Authentication service class."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Token payload data
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, 
                self.settings.secret_key, 
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token data
            
        Raises:
            HTTPException: If token is invalid
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                self.settings.secret_key, 
                algorithms=[self.algorithm]
            )
            
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")
            
            if user_id is None:
                raise credentials_exception
                
            return TokenData(user_id=user_id, email=email, role=role)
            
        except jwt.PyJWTError as e:
            logger.warning(f"JWT decode error: {e}")
            raise credentials_exception
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            # In a real implementation, this would query the database
            # For now, we'll simulate user lookup
            from src.models.database import get_db_session
            
            async with get_db_session() as db:
                user = await db.query(User).filter(User.email == email).first()
                
                if not user:
                    return None
                
                if not self.verify_password(password, user.hashed_password):
                    return None
                
                return user
                
        except Exception as e:
            logger.error(f"User authentication error: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            from src.models.database import get_db_session
            
            async with get_db_session() as db:
                user = await db.query(User).filter(User.id == user_id).first()
                return user
                
        except Exception as e:
            logger.error(f"User lookup error: {e}")
            return None


# Global auth service instance
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP bearer credentials
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    token_data = auth_service.verify_token(credentials.credentials)
    user = await auth_service.get_user_by_id(token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role.value < required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


# Convenience functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token (convenience function)."""
    return auth_service.create_access_token(data, expires_delta)


# API Endpoints
@auth_router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        JWT token for the new user
    """
    try:
        # Check if user already exists
        from src.models.database import get_db_session
        
        async with get_db_session() as db:
            existing_user = await db.query(User).filter(User.email == user_data.email).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            hashed_password = auth_service.get_password_hash(user_data.password)
            
            new_user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=True
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Create access token
            access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
            access_token = auth_service.create_access_token(
                data={
                    "sub": str(new_user.id),
                    "email": new_user.email,
                    "role": new_user.role.value
                },
                expires_delta=access_token_expires
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=auth_service.access_token_expire_minutes * 60,
                user_id=str(new_user.id),
                role=new_user.role.value
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@auth_router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """
    Authenticate user and return JWT token.
    
    Args:
        login_data: User login credentials
        
    Returns:
        JWT token
    """
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,
        user_id=str(user.id),
        role=user.role.value
    )


@auth_router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """Refresh JWT token."""
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={
            "sub": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,
        user_id=str(current_user.id),
        role=current_user.role.value
    )