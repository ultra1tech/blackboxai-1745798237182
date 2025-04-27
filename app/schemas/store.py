from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl
from app.models.store import StoreStatus

class StoreBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: str
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    default_language: Optional[str] = "en"
    default_currency: Optional[str] = "USD"

class StoreCreate(StoreBase):
    """Schema for creating a store"""
    pass

class StoreUpdate(BaseModel):
    """Schema for updating a store"""
    name: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    default_language: Optional[str] = None
    default_currency: Optional[str] = None
    supported_languages: Optional[List[str]] = None

class StoreInDBBase(StoreBase):
    """Base schema for store in database"""
    id: int
    owner_id: int
    status: StoreStatus
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    total_products: int
    total_orders: int
    average_rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class StoreResponse(StoreInDBBase):
    """Schema for store response"""
    pass

class StoreList(BaseModel):
    """Schema for list of stores"""
    stores: List[StoreResponse]

class StoreSearchResults(BaseModel):
    """Schema for store search results"""
    total: int
    stores: List[StoreResponse]
    skip: int
    limit: int

class StoreStats(BaseModel):
    """Schema for store statistics"""
    total_products: int
    total_orders: int
    total_revenue: float
    average_rating: float
    active_products: int
    pending_orders: int
    completed_orders: int

class StoreDashboard(BaseModel):
    """Schema for store dashboard data"""
    store: StoreResponse
    stats: StoreStats
    recent_orders: List[dict]  # We'll define Order schema later
    top_products: List[dict]  # We'll define Product schema later
    revenue_chart: dict  # Example: {"labels": [...], "data": [...]}
