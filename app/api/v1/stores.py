from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.store import Store, StoreStatus
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    StoreList,
    StoreSearchResults
)
from app.utils.file_upload import save_upload

router = APIRouter()

@router.post("/", response_model=StoreResponse)
async def create_store(
    *,
    db: Session = Depends(get_db),
    store_in: StoreCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new store.
    """
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create stores"
        )
    
    # Check if user already has a store
    if db.query(Store).filter(Store.owner_id == current_user.id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a store"
        )
    
    store = Store(
        owner_id=current_user.id,
        name=store_in.name,
        description=store_in.description,
        country=store_in.country,
        city=store_in.city,
        address=store_in.address,
        postal_code=store_in.postal_code,
        phone=store_in.phone,
        email=store_in.email or current_user.email,
        website=store_in.website,
        status=StoreStatus.PENDING
    )
    
    db.add(store)
    db.commit()
    db.refresh(store)
    return store

@router.get("/me", response_model=StoreResponse)
async def get_my_store(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user's store.
    """
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    return store

@router.put("/me", response_model=StoreResponse)
async def update_store(
    *,
    db: Session = Depends(get_db),
    store_in: StoreUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user's store.
    """
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Update store attributes
    for field, value in store_in.dict(exclude_unset=True).items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    return store

@router.post("/me/logo", response_model=StoreResponse)
async def upload_store_logo(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload store logo.
    """
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    logo_url = await save_upload(file, "store_logos")
    store.logo_url = logo_url
    db.commit()
    db.refresh(store)
    return store

@router.get("/search", response_model=StoreSearchResults)
async def search_stores(
    *,
    db: Session = Depends(get_db),
    query: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Search stores by name, description, or country.
    """
    query_filter = []
    
    if query:
        query_filter.append(
            or_(
                Store.name.ilike(f"%{query}%"),
                Store.description.ilike(f"%{query}%")
            )
        )
    
    if country:
        query_filter.append(Store.country == country)
    
    # Only return active stores
    query_filter.append(Store.status == StoreStatus.ACTIVE)
    
    stores = db.query(Store).filter(*query_filter)
    
    total = stores.count()
    stores = stores.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "stores": stores,
        "skip": skip,
        "limit": limit
    }

@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get store by ID.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    if store.status != StoreStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    return store
