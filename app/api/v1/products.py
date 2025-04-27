from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.store import Store, StoreStatus
from app.models.product import Product, ProductStatus
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
    ProductSearchResults
)
from app.utils.file_upload import save_upload

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create new product."""
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create products"
        )
    
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if not store or store.status != StoreStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active store required to create products"
        )
    
    product = Product(
        store_id=store.id,
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        currency=product_in.currency or store.default_currency,
        category=product_in.category,
        subcategory=product_in.subcategory,
        stock_quantity=product_in.stock_quantity,
        sku=product_in.sku,
        weight=product_in.weight,
        dimensions=product_in.dimensions,
        status=ProductStatus.ACTIVE if product_in.stock_quantity > 0 else ProductStatus.OUT_OF_STOCK
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=ProductSearchResults)
async def search_products(
    *,
    db: Session = Depends(get_db),
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    store_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Search products with filters."""
    query_filter = [Product.status == ProductStatus.ACTIVE]
    
    if query:
        query_filter.append(
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%")
            )
        )
    
    if category:
        query_filter.append(Product.category == category)
    
    if min_price is not None:
        query_filter.append(Product.price >= min_price)
    
    if max_price is not None:
        query_filter.append(Product.price <= max_price)
    
    if store_id:
        query_filter.append(Product.store_id == store_id)
    
    products = db.query(Product).filter(*query_filter)
    total = products.count()
    products = products.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "products": products,
        "skip": skip,
        "limit": limit
    }

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.status == ProductStatus.DELETED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    store = db.query(Store).filter(Store.id == product.store_id).first()
    if store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    if product.stock_quantity == 0:
        product.status = ProductStatus.OUT_OF_STOCK
    elif product.status == ProductStatus.OUT_OF_STOCK and product.stock_quantity > 0:
        product.status = ProductStatus.ACTIVE
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    store = db.query(Store).filter(Store.id == product.store_id).first()
    if store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product.status = ProductStatus.DELETED
    db.commit()
    return product

@router.post("/{product_id}/images")
async def upload_product_images(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Upload product images."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    store = db.query(Store).filter(Store.id == product.store_id).first()
    if store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    image_urls = []
    for file in files:
        image_url = await save_upload(file, f"products/{product_id}")
        image_urls.append(image_url)
    
    # Update product images
    current_images = product.images or []
    product.images = current_images + image_urls
    if not product.main_image and image_urls:
        product.main_image = image_urls[0]
    
    db.commit()
    db.refresh(product)
    return {"status": "success", "images": image_urls}
