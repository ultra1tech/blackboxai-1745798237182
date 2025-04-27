from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.store import Store, StoreStatus
from app.models.order import Order, OrderStatus
from app.models.review import Review, ReviewStatus
from app.schemas.admin import (
    AdminStats,
    UserList,
    StoreList,
    OrderList,
    ReviewList,
    StoreApproval
)

router = APIRouter()

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
) -> Any:
    """Get admin dashboard statistics."""
    stats = {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_sellers": db.query(func.count(User.id)).filter(User.role == UserRole.SELLER).scalar(),
        "total_buyers": db.query(func.count(User.id)).filter(User.role == UserRole.BUYER).scalar(),
        "pending_sellers": db.query(func.count(Store.id)).filter(Store.status == StoreStatus.PENDING).scalar(),
        "active_stores": db.query(func.count(Store.id)).filter(Store.status == StoreStatus.ACTIVE).scalar(),
        "total_orders": db.query(func.count(Order.id)).scalar(),
        "pending_orders": db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PENDING).scalar(),
        "total_revenue": db.query(func.sum(Order.total_amount)).filter(Order.status != OrderStatus.CANCELLED).scalar() or 0.0,
        "pending_reviews": db.query(func.count(Review.id)).filter(Review.status == ReviewStatus.PENDING).scalar()
    }
    return stats

@router.get("/users", response_model=UserList)
async def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get list of users with filters."""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "users": users,
        "skip": skip,
        "limit": limit
    }

@router.get("/stores", response_model=StoreList)
async def get_stores(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
    status: Optional[StoreStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get list of stores with filters."""
    query = db.query(Store)
    
    if status:
        query = query.filter(Store.status == status)
    
    total = query.count()
    stores = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "stores": stores,
        "skip": skip,
        "limit": limit
    }

@router.put("/stores/{store_id}/approval", response_model=StoreApproval)
async def approve_store(
    *,
    db: Session = Depends(get_db),
    store_id: int,
    approval: StoreApproval,
    _: User = Depends(get_admin_user)
) -> Any:
    """Approve or reject store."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    store.status = approval.status
    if store.status == StoreStatus.ACTIVE:
        # Also activate the seller's account
        seller = db.query(User).filter(User.id == store.owner_id).first()
        if seller:
            seller.status = UserStatus.ACTIVE
    
    db.commit()
    db.refresh(store)
    return approval

@router.get("/orders", response_model=OrderList)
async def get_orders(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
    status: Optional[OrderStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get list of orders with filters."""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "orders": orders,
        "skip": skip,
        "limit": limit
    }

@router.get("/reviews", response_model=ReviewList)
async def get_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
    status: Optional[ReviewStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get list of reviews with filters."""
    query = db.query(Review)
    
    if status:
        query = query.filter(Review.status == status)
    
    total = query.count()
    reviews = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "reviews": reviews,
        "skip": skip,
        "limit": limit
    }

@router.put("/reviews/{review_id}/status")
async def update_review_status(
    *,
    db: Session = Depends(get_db),
    review_id: int,
    status: ReviewStatus,
    _: User = Depends(get_admin_user)
) -> Any:
    """Update review status (approve/reject)."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.status = status
    if status == ReviewStatus.PUBLISHED:
        review.published_at = db.func.now()
    
    db.commit()
    db.refresh(review)
    
    # Update product rating if review status changed
    if status in [ReviewStatus.PUBLISHED, ReviewStatus.REJECTED]:
        product = review.product
        if product:
            product.update_rating_stats()
            db.commit()
    
    return {"status": "success", "message": f"Review {status}"}
