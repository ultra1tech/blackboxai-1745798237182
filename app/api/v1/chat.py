from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.chat import Chat, ChatRoom, MessageStatus, MessageType
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRoomResponse,
    ChatList
)

router = APIRouter()

@router.post("/rooms/{user_id}", response_model=ChatRoomResponse)
async def create_chat_room(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create or get existing chat room with another user."""
    # Check if target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check for existing chat room
    chat_room = db.query(ChatRoom).filter(
        or_(
            and_(
                ChatRoom.user1_id == current_user.id,
                ChatRoom.user2_id == user_id
            ),
            and_(
                ChatRoom.user1_id == user_id,
                ChatRoom.user2_id == current_user.id
            )
        )
    ).first()
    
    if not chat_room:
        # Create new chat room
        chat_room = ChatRoom(
            user1_id=current_user.id,
            user2_id=user_id
        )
        db.add(chat_room)
        db.commit()
        db.refresh(chat_room)
    
    return chat_room

@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_chat_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all chat rooms for current user."""
    chat_rooms = db.query(ChatRoom).filter(
        or_(
            ChatRoom.user1_id == current_user.id,
            ChatRoom.user2_id == current_user.id
        )
    ).all()
    return chat_rooms

@router.get("/rooms/{room_id}/messages", response_model=ChatList)
async def get_chat_messages(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> Any:
    """Get messages for a chat room."""
    # Verify room exists and user has access
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    if current_user.id not in [chat_room.user1_id, chat_room.user2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get messages
    messages = db.query(Chat).filter(
        and_(
            or_(
                Chat.sender_id == chat_room.user1_id,
                Chat.sender_id == chat_room.user2_id
            ),
            or_(
                Chat.receiver_id == chat_room.user1_id,
                Chat.receiver_id == chat_room.user2_id
            )
        )
    ).order_by(Chat.created_at.desc())
    
    total = messages.count()
    messages = messages.offset(skip).limit(limit).all()
    
    # Update last read timestamp
    if current_user.id == chat_room.user1_id:
        chat_room.user1_last_read = db.func.now()
    else:
        chat_room.user2_last_read = db.func.now()
    
    db.commit()
    
    return {
        "total": total,
        "messages": messages,
        "skip": skip,
        "limit": limit
    }

@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    *,
    room_id: int,
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Send a message in a chat room."""
    # Verify room exists and user has access
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    if current_user.id not in [chat_room.user1_id, chat_room.user2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Determine receiver
    receiver_id = chat_room.user2_id if current_user.id == chat_room.user1_id else chat_room.user1_id
    
    # Create message
    chat_message = Chat(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message_type=message.message_type,
        content=message.content,
        media_url=message.media_url,
        metadata=message.metadata
    )
    
    db.add(chat_message)
    
    # Update chat room
    chat_room.last_message_at = db.func.now()
    
    db.commit()
    db.refresh(chat_message)
    return chat_message

@router.put("/messages/{message_id}/read", response_model=ChatMessageResponse)
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mark a message as read."""
    message = db.query(Chat).filter(Chat.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    message.status = MessageStatus.READ
    message.read_at = db.func.now()
    db.commit()
    db.refresh(message)
    return message

@router.delete("/messages/{message_id}", response_model=ChatMessageResponse)
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete a message (mark as deleted)."""
    message = db.query(Chat).filter(Chat.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    message.status = MessageStatus.DELETED
    db.commit()
    db.refresh(message)
    return message
