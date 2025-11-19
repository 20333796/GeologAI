"""
Security and authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import os

# HTTPAuthCredentials is just a named tuple, we can define it locally if needed
try:
    from fastapi.security import HTTPAuthCredentials
except ImportError:
    # Fallback for older/newer FastAPI versions
    from typing import NamedTuple
    class HTTPAuthCredentials(NamedTuple):
        scheme: str
        credentials: str

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer()


class SecurityUtility:
    """Security utilities for authentication and authorization"""
    
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=SecurityUtility.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode,
            SecurityUtility.SECRET_KEY,
            algorithm=SecurityUtility.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=SecurityUtility.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            SecurityUtility.SECRET_KEY,
            algorithm=SecurityUtility.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                SecurityUtility.SECRET_KEY,
                algorithms=[SecurityUtility.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def verify_access_token(credentials: HTTPAuthCredentials) -> dict:
        """Verify access token from HTTP bearer"""
        token = credentials.credentials
        payload = SecurityUtility.verify_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return payload


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user
    """
    return SecurityUtility.verify_access_token(credentials)


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
