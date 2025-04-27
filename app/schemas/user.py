from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    country: Optional[str] = None
    language: Optional[str] = "en"
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.BUYER
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "full_name": "John Doe",
                "country": "US",
                "language": "en",
                "phone": "+1234567890",
                "role": "buyer"
            }
        }

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "country": "US",
                "language": "en",
                "phone": "+1234567890",
                "profile_image": "path/to/image.jpg"
            }
        }

class UserInDBBase(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDBBase):
    """Response model for user data"""
    store_id: Optional[int] = None
    total_orders: Optional[int] = 0
    total_reviews: Optional[int] = 0
    average_rating: Optional[float] = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "buyer",
                "status": "active",
                "country": "US",
                "language": "en",
                "phone": "+1234567890",
                "profile_image": "path/to/image.jpg",
                "store_id": None,
                "total_orders": 0,
                "total_reviews": 0,
                "average_rating": 0.0,
                "created_at": "2024-03-20T12:00:00Z",
                "updated_at": "2024-03-20T12:00:00Z",
                "last_login": "2024-03-20T12:00:00Z"
            }
        }

class UserWithStore(User):
    """Response model for user data with store information"""
    store: Optional[dict] = None

class UserStats(BaseModel):
    """Statistics for a user"""
    total_orders: int = 0
    total_spent: float = 0.0
    average_order_value: float = 0.0
    total_reviews: int = 0
    average_rating_given: float = 0.0
    wishlist_count: int = 0
    last_order_date: Optional[datetime] = None

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }

class PasswordReset(BaseModel):
    """Schema for password reset"""
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset-token-123",
                "new_password": "newpassword123"
            }
        }
