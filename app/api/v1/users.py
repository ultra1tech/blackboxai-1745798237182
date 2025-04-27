from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User, UserStatus
from app.schemas.user import UserUpdate, User as UserSchema, UserStats
from app.utils.file_upload import save_upload

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update current user information."""
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/avatar")
async def upload_avatar(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Upload user avatar."""
    avatar_url = await save_upload(file, f"users/{current_user.id}")
    current_user.profile_image = avatar_url
    db.commit()
    db.refresh(current_user)
    return {"avatar_url": avatar_url}

@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user statistics."""
    # Calculate user statistics
    stats = UserStats(
        total_orders=len(current_user.orders),
        total_spent=sum(order.total_amount for order in current_user.orders),
        total_reviews=len(current_user.reviews),
        average_rating_given=sum(review.rating for review in current_user.reviews) / len(current_user.reviews) if current_user.reviews else 0.0,
        wishlist_count=len(current_user.wishlist_items)
    )
    
    if current_user.orders:
        stats.average_order_value = stats.total_spent / stats.total_orders
        stats.last_order_date = max(order.created_at for order in current_user.orders)
    
    return stats

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
