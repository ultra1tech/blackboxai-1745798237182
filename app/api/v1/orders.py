from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.order import Order, OrderStatus, OrderItem
from app.models.product import Product, ProductStatus
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderList,
    OrderItemCreate
)

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create new order."""
    # Verify products and calculate totals
    items = []
    subtotal = 0.0
    store_id = None

    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.status != ProductStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} not available"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}"
            )
        
        # All items must be from the same store
        if store_id is None:
            store_id = product.store_id
        elif store_id != product.store_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All products must be from the same store"
            )
        
        item_subtotal = product.current_price * item.quantity
        subtotal += item_subtotal
        
        items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.current_price,
            "subtotal": item_subtotal
        })

    # Calculate shipping and tax
    shipping_cost = order_in.shipping_cost or 0.0
    tax = (subtotal + shipping_cost) * 0.1  # 10% tax example
    total_amount = subtotal + shipping_cost + tax

    # Create order
    order = Order(
        buyer_id=current_user.id,
        store_id=store_id,
        status=OrderStatus.PENDING,
        shipping_address=order_in.shipping_address.dict(),
        shipping_cost=shipping_cost,
        subtotal=subtotal,
        tax=tax,
        total_amount=total_amount,
        currency=items[0]["product"].currency,
        buyer_notes=order_in.notes
    )
    
    db.add(order)
    db.flush()  # Get order ID without committing

    # Create order items and update product stock
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            subtotal=item["subtotal"],
            product_name=item["product"].name,
            product_sku=item["product"].sku
        )
        db.add(order_item)
        
        # Update product stock
        item["product"].stock_quantity -= item["quantity"]
        if item["product"].stock_quantity == 0:
            item["product"].status = ProductStatus.OUT_OF_STOCK

    db.commit()
    db.refresh(order)
    return order

@router.get("/my-orders", response_model=OrderList)
async def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get current user's orders."""
    orders = db.query(Order).filter(Order.buyer_id == current_user.id)
    total = orders.count()
    orders = orders.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "orders": orders,
        "skip": skip,
        "limit": limit
    }

@router.get("/store-orders", response_model=OrderList)
async def get_store_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[OrderStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Get orders for seller's store."""
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a seller"
        )
    
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    query = db.query(Order).filter(Order.store_id == store.id)
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "orders": orders,
        "skip": skip,
        "limit": limit
    }

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.BUYER and order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.SELLER:
        store = db.query(Store).filter(Store.owner_id == current_user.id).first()
        if not store or order.store_id != store.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status: OrderStatus,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update order status (seller only)."""
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can update order status"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if not store or order.store_id != store.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update status and timestamps
    order.status = status
    if status == OrderStatus.SHIPPED:
        order.shipped_at = db.func.now()
    elif status == OrderStatus.DELIVERED:
        order.delivered_at = db.func.now()
    
    db.commit()
    db.refresh(order)
    return order
