from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DELETED = "deleted"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Categories and Tags
    category = Column(String(100), index=True)
    subcategory = Column(String(100), index=True)
    tags = Column(String)  # Comma-separated tags
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(50), unique=True)
    low_stock_threshold = Column(Integer, default=10)
    
    # Media
    images = Column(JSON)  # List of image URLs
    main_image = Column(String)  # URL to main product image
    
    # Status and Visibility
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE)
    featured = Column(Boolean, default=False)
    
    # Pricing
    original_price = Column(Float)  # For displaying discounts
    sale_price = Column(Float)
    sale_start_date = Column(DateTime(timezone=True))
    sale_end_date = Column(DateTime(timezone=True))
    
    # Shipping
    weight = Column(Float)  # in kg
    dimensions = Column(JSON)  # {"length": x, "width": y, "height": z}
    shipping_class = Column(String(50))
    
    # SEO
    meta_title = Column(String(200))
    meta_description = Column(Text)
    
    # Reviews and Ratings
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name}>"

    @property
    def tags_list(self):
        """Convert comma-separated tags string to list"""
        return [tag.strip() for tag in (self.tags or "").split(",") if tag.strip()]

    @tags_list.setter
    def tags_list(self, tags):
        """Convert list of tags to comma-separated string"""
        self.tags = ",".join(tags)

    @property
    def current_price(self):
        """Get the current effective price"""
        if (self.sale_price and self.sale_start_date and self.sale_end_date and
            self.sale_start_date <= func.now() <= self.sale_end_date):
            return self.sale_price
        return self.price

    def update_rating_stats(self):
        """Update average rating and review count"""
        if self.reviews:
            ratings = [review.rating for review in self.reviews if review.status == "published"]
            self.review_count = len(ratings)
            self.average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        else:
            self.review_count = 0
            self.average_rating = 0.0
