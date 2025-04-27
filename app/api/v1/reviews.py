from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.product import Product
from app.models.review import Review, ReviewStatus, ReviewHelpfulVote, WishlistItem
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewList,
    WishlistItemCreate,
    WishlistResponse
)
from app.utils.file_upload import save_upload

router = APIRouter()

# Review endpoints
@router.post("/products/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create new product review."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has already reviewed this product
    existing_review = db.query(Review).filter(
        and_(
            Review.product_id == product_id,
            Review.user_id == current_user.id,
            Review.status != ReviewStatus.DELETED
        )
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=review_in.rating,
        title=review_in.title,
        comment=review_in.comment,
        status=ReviewStatus.PUBLISHED
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Update product rating
    product.update_rating_stats()
    db.commit()
    
    return review

@router.get("/products/{product_id}/reviews", response_model=ReviewList)
async def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get reviews for a product."""
    reviews = db.query(Review).filter(
        and_(
            Review.product_id == product_id,
            Review.status == ReviewStatus.PUBLISHED
        )
    )
    
    total = reviews.count()
    reviews = reviews.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "reviews": reviews,
        "skip": skip,
        "limit": limit
    }

@router.post("/reviews/{review_id}/helpful", response_model=ReviewResponse)
async def mark_review_helpful(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mark a review as helpful."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user has already marked this review as helpful
    existing_vote = db.query(ReviewHelpfulVote).filter(
        and_(
            ReviewHelpfulVote.review_id == review_id,
            ReviewHelpfulVote.user_id == current_user.id
        )
    ).first()
    
    if existing_vote:
        # Remove the vote
        db.delete(existing_vote)
        review.helpful_votes -= 1
    else:
        # Add new vote
        vote = ReviewHelpfulVote(
            review_id=review_id,
            user_id=current_user.id
        )
        db.add(vote)
        review.helpful_votes += 1
    
    db.commit()
    db.refresh(review)
    return review

# Wishlist endpoints
@router.post("/wishlist", response_model=WishlistResponse)
async def add_to_wishlist(
    *,
    db: Session = Depends(get_db),
    wishlist_item: WishlistItemCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Add product to wishlist."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == wishlist_item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already in wishlist
    existing_item = db.query(WishlistItem).filter(
        and_(
            WishlistItem.user_id == current_user.id,
            WishlistItem.product_id == wishlist_item.product_id
        )
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in wishlist"
        )
    
    wishlist_item = WishlistItem(
        user_id=current_user.id,
        product_id=product.id,
        price_when_added=product.current_price,
        notify_on_price_drop=wishlist_item.notify_on_price_drop,
        price_drop_threshold=wishlist_item.price_drop_threshold,
        notes=wishlist_item.notes
    )
    
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

@router.get("/wishlist", response_model=List[WishlistResponse])
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get user's wishlist."""
    return db.query(WishlistItem).filter(WishlistItem.user_id == current_user.id).all()

@router.delete("/wishlist/{product_id}", response_model=WishlistResponse)
async def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Remove product from wishlist."""
    wishlist_item = db.query(WishlistItem).filter(
        and_(
            WishlistItem.user_id == current_user.id,
            WishlistItem.product_id == product_id
        )
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in wishlist"
        )
    
    db.delete(wishlist_item)
    db.commit()
    return wishlist_item
