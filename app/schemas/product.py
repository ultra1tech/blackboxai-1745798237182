from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, constr, confloat, conint
from app.models.product import ProductStatus

class ProductBase(BaseModel):
    name: constr(min_length=1, max_length=200)
    description: Optional[str] = None
    price: confloat(gt=0)
    currency: Optional[str] = "USD"
    category: str
    subcategory: Optional[str] = None
    stock_quantity: conint(ge=0)
    sku: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    low_stock_threshold: Optional[int] = 10

class ProductCreate(ProductBase):
    """Schema for creating a product"""
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[str] = None
    price: Optional[confloat(gt=0)] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    stock_quantity: Optional[conint(ge=0)] = None
    sku: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    low_stock_threshold: Optional[int] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    featured: Optional[bool] = None
    sale_price: Optional[float] = None
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None

class ProductInDBBase(ProductBase):
    """Base schema for product in database"""
    id: int
    store_id: int
    status: ProductStatus
    images: Optional[List[str]] = None
    main_image: Optional[str] = None
    featured: bool
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None
    average_rating: float
    review_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProductResponse(ProductInDBBase):
    """Schema for product response"""
    store_name: Optional[str] = None
    current_price: float

class ProductList(BaseModel):
    """Schema for list of products"""
    products: List[ProductResponse]

class ProductSearchResults(BaseModel):
    """Schema for product search results"""
    total: int
    products: List[ProductResponse]
    skip: int
    limit: int

class ProductStats(BaseModel):
    """Schema for product statistics"""
    total_views: int
    total_sales: int
    revenue: float
    average_rating: float
    review_count: int
    in_wishlist_count: int

class ProductWithReviews(ProductResponse):
    """Schema for product with reviews"""
    reviews: List[dict]  # We'll define Review schema later

class ProductImage(BaseModel):
    """Schema for product image"""
    url: str
    is_main: bool = False
    order: int = 0
