from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, conint, confloat
from app.models.order import OrderStatus, PaymentStatus, PaymentMethod

class ShippingAddress(BaseModel):
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: str

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: conint(gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: ShippingAddress
    shipping_cost: Optional[float] = None
    payment_method: PaymentMethod
    notes: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: Optional[str]
    quantity: int
    unit_price: float
    subtotal: float
    created_at: datetime

    class Config:
        orm_mode = True

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    seller_notes: Optional[str] = None

class OrderInDBBase(BaseModel):
    id: int
    order_number: str
    buyer_id: int
    store_id: int
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    currency: str
    subtotal: float
    shipping_cost: float
    tax: float
    discount: float
    total_amount: float
    shipping_address: Dict
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    buyer_notes: Optional[str] = None
    seller_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class OrderResponse(OrderInDBBase):
    items: List[OrderItemResponse]
    buyer_name: Optional[str] = None
    store_name: Optional[str] = None

class OrderList(BaseModel):
    total: int
    orders: List[OrderResponse]
    skip: int
    limit: int

class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    average_order_value: float

class PaymentDetails(BaseModel):
    payment_method: PaymentMethod
    transaction_id: str
    amount: float
    currency: str
    status: PaymentStatus
    payment_date: datetime
    billing_address: Optional[Dict] = None
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    notes: Optional[str] = None

class OrderTimeline(BaseModel):
    created: datetime
    paid: Optional[datetime] = None
    processed: Optional[datetime] = None
    shipped: Optional[datetime] = None
    delivered: Optional[datetime] = None
    cancelled: Optional[datetime] = None
    refunded: Optional[datetime] = None
