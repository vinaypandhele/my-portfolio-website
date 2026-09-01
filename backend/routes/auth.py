"""
Authentication Routes - User Login, Signup, and JWT Token Management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Router
router = APIRouter()

# ==========================================
# Pydantic Models
# ==========================================

class UserSignup(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    created_at: datetime

# Mock user database (replace with actual database)
fake_users_db = {}

# ==========================================
# Helper Functions
# ==========================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify JWT token and return current user"""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    # Get user from database (mock implementation)
    user = fake_users_db.get(email)
    if user is None:
        raise credential_exception
    return user

# ==========================================
# Authentication Endpoints
# ==========================================

@router.post("/signup", response_model=dict)
async def signup(user_data: UserSignup):
    """
    User registration endpoint
    
    Args:
        user_data: User signup information
        
    Returns:
        Success message with user data
    """
    try:
        # Check if user already exists
        if user_data.email in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = f"user_{len(fake_users_db) + 1}"
        hashed_password = hash_password(user_data.password)
        
        user = {
            "id": user_id,
            "firstName": user_data.firstName,
            "lastName": user_data.lastName,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        fake_users_db[user_data.email] = user
        
        logger.info(f"New user registered: {user_data.email}")
        
        return {
            "success": True,
            "message": "Account created successfully",
            "user": {
                "id": user["id"],
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "email": user["email"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating account"
        )

@router.post("/login", response_model=dict)
async def login(user_data: UserLogin):
    """
    User login endpoint
    
    Args:
        user_data: User login credentials
        
    Returns:
        JWT token and user information
    """
    try:
        # Find user
        user = fake_users_db.get(user_data.email)
        
        if not user or not verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email})
        
        logger.info(f"User logged in: {user_data.email}")
        
        return {
            "success": True,
            "message": "Login successful",
            "token": access_token,
            "user": {
                "id": user["id"],
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "email": user["email"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout endpoint
    
    Returns:
        Logout success message
    """
    logger.info(f"User logged out: {current_user['email']}")
    return {
        "success": True,
        "message": "Logout successful"
    }

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Returns:
        Current user data
    """
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "firstName": current_user["firstName"],
            "lastName": current_user["lastName"],
            "email": current_user["email"],
            "created_at": current_user["created_at"].isoformat()
        }
    }

@router.post("/forgot-password")
async def forgot_password(email: EmailStr):
    """
    Forgot password endpoint - Send reset link
    
    Args:
        email: User email address
        
    Returns:
        Success message
    """
    try:
        user = fake_users_db.get(email)
        
        if not user:
            # Don't reveal if email exists for security
            return {
                "success": True,
                "message": "If email exists, password reset link sent"
            }
        
        # Generate reset token (implement email sending here)
        reset_token = create_access_token(
            data={"sub": email, "type": "reset"},
            expires_delta=timedelta(hours=1)
        )
        
        logger.info(f"Password reset requested for: {email}")
        
        return {
            "success": True,
            "message": "Password reset link sent to email",
            "reset_token": reset_token  # Remove in production, send via email instead
        }
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing request"
        )

@router.post("/reset-password")
async def reset_password(email: EmailStr, token: str, new_password: str):
    """
    Reset password using token
    
    Args:
        email: User email
        token: Reset token
        new_password: New password
        
    Returns:
        Success message
    """
    try:
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_email = payload.get("sub")
            token_type = payload.get("type")
            
            if token_email != email or token_type != "reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        # Update password
        user = fake_users_db.get(email)
        if user:
            user["hashed_password"] = hash_password(new_password)
            logger.info(f"Password reset successful for: {email}")
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error resetting password"
        )
