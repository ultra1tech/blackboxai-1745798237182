from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.user import UserRole, UserStatus
from app.models.store import StoreStatus
from app.models.order import OrderStatus
from app.models.review import ReviewStatus
from app.schemas.user import User
from app.schemas.store import StoreResponse
from app.schemas.order import OrderResponse
from app.schemas.review import ReviewResponse

class AdminStats(BaseModel):
    """Schema for admin dashboard statistics"""
    total_users: int
    total_sellers: int
    total_buyers: int
    pending_sellers: int
    active_stores: int
    total_orders: int
    pending_orders: int
    total_revenue: float
    pending_reviews: int

class UserList(BaseModel):
    """Schema for list of users"""
    total: int
    users: List[User]
    skip: int
    limit: int

class StoreList(BaseModel):
    """Schema for list of stores"""
    total: int
    stores: List[StoreResponse]
    skip: int
    limit: int

class OrderList(BaseModel):
    """Schema for list of orders"""
    total: int
    orders: List[OrderResponse]
    skip: int
    limit: int

class ReviewList(BaseModel):
    """Schema for list of reviews"""
    total: int
    reviews: List[ReviewResponse]
    skip: int
    limit: int

class StoreApproval(BaseModel):
    """Schema for store approval/rejection"""
    status: StoreStatus
    notes: Optional[str] = None

class UserStatusUpdate(BaseModel):
    """Schema for updating user status"""
    status: UserStatus
    notes: Optional[str] = None

class ReviewStatusUpdate(BaseModel):
    """Schema for updating review status"""
    status: ReviewStatus
    notes: Optional[str] = None

class AdminDashboardStats(BaseModel):
    """Schema for detailed admin dashboard statistics"""
    users: dict = {
        "total": 0,
        "active": 0,
        "pending": 0,
        "suspended": 0,
        "new_today": 0,
        "new_this_week": 0,
        "new_this_month": 0
    }
    
    stores: dict = {
        "total": 0,
        "active": 0,
        "pending": 0,
        "suspended": 0,
        "new_today": 0,
        "new_this_week": 0,
        "new_this_month": 0
    }
    
    orders: dict = {
        "total": 0,
        "pending": 0,
        "processing": 0,
        "shipped": 0,
        "delivered": 0,
        "cancelled": 0,
        "total_today": 0,
        "total_this_week": 0,
        "total_this_month": 0
    }
    
    revenue: dict = {
        "total": 0.0,
        "today": 0.0,
        "this_week": 0.0,
        "this_month": 0.0,
        "average_order_value": 0.0
    }
    
    products: dict = {
        "total": 0,
        "active": 0,
        "out_of_stock": 0,
        "low_stock": 0
    }

class AdminActionLog(BaseModel):
    """Schema for admin action logs"""
    id: int
    admin_id: int
    action: str
    entity_type: str
    entity_id: int
    previous_state: Optional[dict] = None
    new_state: Optional[dict] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class AdminActionLogList(BaseModel):
    """Schema for list of admin action logs"""
    total: int
    logs: List[AdminActionLog]
    skip: int
    limit: int

class SystemMetrics(BaseModel):
    """Schema for system performance metrics"""
    api_requests: dict = {
        "total": 0,
        "success": 0,
        "errors": 0,
        "average_response_time": 0.0
    }
    
    database: dict = {
        "connections": 0,
        "active_queries": 0,
        "slow_queries": 0
    }
    
    storage: dict = {
        "total": 0,
        "used": 0,
        "available": 0
    }
    
    cache: dict = {
        "hit_rate": 0.0,
        "miss_rate": 0.0,
        "size": 0
    }
