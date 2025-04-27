from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"
    DELETED = "deleted"

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))  # Optional: link to order
    
    # Review Content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200))
    comment = Column(Text)
    images = Column(JSON)  # List of image URLs
    
    # Review Status
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    verified_purchase = Column(Boolean, default=False)
    
    # Engagement Metrics
    helpful_votes = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    
    # Admin/Moderation
    admin_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    helpful_votes_users = relationship(
        "ReviewHelpfulVote",
        back_populates="review",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Review {self.id} - {self.rating} stars>"

class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="helpful_votes_users")
    
    class Config:
        unique_together = (("review_id", "user_id"),)

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Additional Info
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)  # Optional user notes
    
    # Price tracking
    price_when_added = Column(Float)
    notify_on_price_drop = Column(Boolean, default=False)
    price_drop_threshold = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")
    
    def __repr__(self):
        return f"<WishlistItem {self.user_id} - {self.product_id}>"

    class Config:
        unique_together = (("user_id", "product_id"),)
