from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SELLER = "seller"
    BUYER = "buyer"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    
    # Profile information
    full_name = Column(String(100))
    phone = Column(String(20))
    country = Column(String(100))
    language = Column(String(10), default="en")
    profile_image = Column(String)  # URL to profile image
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    store = relationship("Store", back_populates="owner", uselist=False)
    orders = relationship("Order", back_populates="buyer")
    reviews = relationship("Review", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user")
    
    # Chat relationships
    sent_messages = relationship(
        "Chat",
        foreign_keys="Chat.sender_id",
        back_populates="sender"
    )
    received_messages = relationship(
        "Chat",
        foreign_keys="Chat.receiver_id",
        back_populates="receiver"
    )

    def __repr__(self):
        return f"<User {self.email}>"
