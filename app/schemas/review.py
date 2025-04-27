from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, conint
from app.models.review import ReviewStatus

class ReviewBase(BaseModel):
    rating: conint(ge=1, le=5)
    title: Optional[str] = None
    comment: str
    images: Optional[List[str]] = None

class ReviewCreate(ReviewBase):
    """Schema for creating a review"""
    pass

class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    title: Optional[str] = None
    comment: Optional[str] = None
    images: Optional[List[str]] = None

class ReviewInDBBase(ReviewBase):
    """Base schema for review in database"""
    id: int
    user_id: int
    product_id: int
    status: ReviewStatus
    verified_purchase: bool
    helpful_votes: int
    report_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ReviewResponse(ReviewInDBBase):
    """Schema for review response"""
    user_name: Optional[str] = None
    user_image: Optional[str] = None

class ReviewList(BaseModel):
    """Schema for list of reviews"""
    total: int
    reviews: List[ReviewResponse]
    skip: int
    limit: int

class ReviewStats(BaseModel):
    """Schema for review statistics"""
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[int, int]  # e.g., {5: 10, 4: 5, 3: 3, 2: 1, 1: 1}

# Wishlist Schemas
class WishlistItemBase(BaseModel):
    product_id: int
    notify_on_price_drop: Optional[bool] = False
    price_drop_threshold: Optional[float] = None
    notes: Optional[str] = None

class WishlistItemCreate(WishlistItemBase):
    """Schema for creating a wishlist item"""
    pass

class WishlistItemUpdate(BaseModel):
    """Schema for updating a wishlist item"""
    notify_on_price_drop: Optional[bool] = None
    price_drop_threshold: Optional[float] = None
    notes: Optional[str] = None

class WishlistItemInDBBase(WishlistItemBase):
    """Base schema for wishlist item in database"""
    id: int
    user_id: int
    price_when_added: float
    added_at: datetime

    class Config:
        orm_mode = True

class WishlistResponse(WishlistItemInDBBase):
    """Schema for wishlist item response"""
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    current_price: Optional[float] = None
    price_difference: Optional[float] = None
    in_stock: Optional[bool] = None

class WishlistList(BaseModel):
    """Schema for list of wishlist items"""
    total: int
    items: List[WishlistResponse]

class WishlistStats(BaseModel):
    """Schema for wishlist statistics"""
    total_items: int
    total_value: float
    items_on_sale: int
    items_out_of_stock: int
    average_price: float

class ReviewHelpfulVote(BaseModel):
    """Schema for review helpful vote"""
    review_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
