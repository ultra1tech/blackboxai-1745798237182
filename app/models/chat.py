from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class MessageStatus(str, enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DELETED = "deleted"

class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message Content
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    media_url = Column(String)  # For image/file messages
    message_metadata = Column(JSON)  # Additional message metadata (renamed from metadata)
    
    # Message Status
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    is_edited = Column(Boolean, default=False)
    
    # Context References
    order_id = Column(Integer, ForeignKey("orders.id"))  # Optional: link to order
    product_id = Column(Integer, ForeignKey("products.id"))  # Optional: link to product
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )
    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages"
    )
    
    def __repr__(self):
        return f"<Chat {self.id} - {self.message_type}>"

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Room Status
    last_message_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Metadata
    user1_last_read = Column(DateTime(timezone=True))
    user2_last_read = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ChatRoom {self.id} - {self.user1_id} & {self.user2_id}>"

    class Config:
        unique_together = (("user1_id", "user2_id"),)

    @property
    def unread_count_user1(self):
        """Get number of unread messages for user1"""
        if not self.user1_last_read:
            return Chat.query.filter(
                Chat.sender_id == self.user2_id,
                Chat.receiver_id == self.user1_id,
                Chat.created_at > self.created_at
            ).count()
        return Chat.query.filter(
            Chat.sender_id == self.user2_id,
            Chat.receiver_id == self.user1_id,
            Chat.created_at > self.user1_last_read
        ).count()

    @property
    def unread_count_user2(self):
        """Get number of unread messages for user2"""
        if not self.user2_last_read:
            return Chat.query.filter(
                Chat.sender_id == self.user1_id,
                Chat.receiver_id == self.user2_id,
                Chat.created_at > self.created_at
            ).count()
        return Chat.query.filter(
            Chat.sender_id == self.user1_id,
            Chat.receiver_id == self.user2_id,
            Chat.created_at > self.user2_last_read
        ).count()
