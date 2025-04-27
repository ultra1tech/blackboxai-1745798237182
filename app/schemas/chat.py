from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.chat import MessageStatus, MessageType

class ChatMessageBase(BaseModel):
    message_type: MessageType = MessageType.TEXT
    content: str
    media_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    pass

class ChatMessageUpdate(BaseModel):
    """Schema for updating a chat message"""
    content: Optional[str] = None
    media_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageInDBBase(ChatMessageBase):
    """Base schema for chat message in database"""
    id: int
    sender_id: int
    receiver_id: int
    status: MessageStatus
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ChatMessageResponse(ChatMessageInDBBase):
    """Schema for chat message response"""
    sender_name: Optional[str] = None
    sender_image: Optional[str] = None
    is_sender: Optional[bool] = None

class ChatRoomBase(BaseModel):
    user1_id: int
    user2_id: int

class ChatRoomCreate(ChatRoomBase):
    """Schema for creating a chat room"""
    pass

class ChatRoomInDBBase(ChatRoomBase):
    """Base schema for chat room in database"""
    id: int
    last_message_at: Optional[datetime] = None
    is_active: bool
    user1_last_read: Optional[datetime] = None
    user2_last_read: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ChatRoomResponse(ChatRoomInDBBase):
    """Schema for chat room response"""
    other_user_name: str
    other_user_image: Optional[str] = None
    last_message: Optional[ChatMessageResponse] = None
    unread_count: int

class ChatList(BaseModel):
    """Schema for list of chat messages"""
    total: int
    messages: List[ChatMessageResponse]
    skip: int
    limit: int

class ChatRoomList(BaseModel):
    """Schema for list of chat rooms"""
    total: int
    rooms: List[ChatRoomResponse]
    skip: int
    limit: int

class ChatStats(BaseModel):
    """Schema for chat statistics"""
    total_messages: int
    unread_messages: int
    active_chats: int
    last_activity: Optional[datetime] = None

class ChatNotification(BaseModel):
    """Schema for chat notifications"""
    room_id: int
    message: ChatMessageResponse
    sender_name: str
    sender_image: Optional[str] = None
