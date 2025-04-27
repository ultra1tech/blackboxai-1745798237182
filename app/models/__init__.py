from app.db.base import Base
from app.models.user import User, UserRole, UserStatus
from app.models.store import Store, StoreStatus
from app.models.product import Product, ProductStatus
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus, PaymentMethod
from app.models.review import Review, ReviewStatus, ReviewHelpfulVote, WishlistItem
from app.models.chat import Chat, ChatRoom, MessageStatus, MessageType

# Import all models here to ensure they are registered with SQLAlchemy
__all__ = [
    "Base",
    "User",
    "UserRole",
    "UserStatus",
    "Store",
    "StoreStatus",
    "Product",
    "ProductStatus",
    "Order",
    "OrderItem",
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    "Review",
    "ReviewStatus",
    "ReviewHelpfulVote",
    "WishlistItem",
    "Chat",
    "ChatRoom",
    "MessageStatus",
    "MessageType",
]

# This ensures all models are properly registered with SQLAlchemy
# and can be used for creating tables and relationships
