from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class StoreStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Store Information
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True)
    description = Column(Text)
    logo_url = Column(String)
    banner_url = Column(String)
    status = Column(Enum(StoreStatus), default=StoreStatus.PENDING)
    
    # Contact Information
    email = Column(String)
    phone = Column(String(20))
    website = Column(String)
    
    # Location Information
    country = Column(String(100), nullable=False)
    city = Column(String(100))
    address = Column(Text)
    postal_code = Column(String(20))
    
    # Store Settings
    default_language = Column(String(10), default="en")
    supported_languages = Column(String)  # Comma-separated list of language codes
    default_currency = Column(String(3), default="USD")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Store Metrics
    total_products = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Relationships
    owner = relationship("User", back_populates="store")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="store")
    
    def __repr__(self):
        return f"<Store {self.name}>"

    @property
    def supported_languages_list(self):
        """Convert comma-separated languages string to list"""
        return [lang.strip() for lang in (self.supported_languages or "").split(",") if lang.strip()]

    @supported_languages_list.setter
    def supported_languages_list(self, languages):
        """Convert list of languages to comma-separated string"""
        self.supported_languages = ",".join(languages)
