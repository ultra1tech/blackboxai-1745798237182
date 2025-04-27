from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: Optional[str] = None
    role: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sub": "user@example.com",
                "role": "buyer"
            }
        }

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "strongpassword123"
            }
        }

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
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
                "new_password": "newstrongpassword123"
            }
        }

class ChangePasswordRequest(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "currentpassword123",
                "new_password": "newstrongpassword123"
            }
        }

class AuthResponse(BaseModel):
    """Schema for generic auth response"""
    message: str
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }
