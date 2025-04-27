import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.models.store import Store, StoreStatus
from app.models.product import Product, ProductStatus
from app.models.order import Order, OrderStatus, OrderItem, PaymentStatus, PaymentMethod

def init_db(db: Session) -> None:
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    # Check if admin user exists
    admin = db.query(User).filter(User.email == "admin@baw.com").first()
    if not admin:
        print("Creating admin user...")
        admin = User(
            email="admin@baw.com",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        db.add(admin)
        db.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists")

    # Check if sample seller exists
    seller = db.query(User).filter(User.email == "seller@baw.com").first()
    if not seller:
        print("Creating sample seller...")
        seller = User(
            email="seller@baw.com",
            password_hash=get_password_hash("seller123"),
            full_name="Sample Seller",
            role=UserRole.SELLER,
            status=UserStatus.ACTIVE,
            country="US",
            phone="+1234567890"
        )
        db.add(seller)
        db.commit()
        print("Sample seller created successfully!")
    else:
        print("Sample seller already exists")

    # Check if sample buyer exists
    buyer = db.query(User).filter(User.email == "buyer@baw.com").first()
    if not buyer:
        print("Creating sample buyer...")
        buyer = User(
            email="buyer@baw.com",
            password_hash=get_password_hash("buyer123"),
            full_name="Sample Buyer",
            role=UserRole.BUYER,
            status=UserStatus.ACTIVE,
            country="US",
            phone="+1987654321"
        )
        db.add(buyer)
        db.commit()
        print("Sample buyer created successfully!")
    else:
        print("Sample buyer already exists")

    # Check if sample store exists
    store = db.query(Store).filter(Store.owner_id == seller.id).first()
    if not store:
        print("Creating sample store...")
        store = Store(
            owner_id=seller.id,
            name="Sample Store",
            description="A sample store selling various products",
            status=StoreStatus.ACTIVE,
            country="US",
            city="New York",
            email=seller.email,
            phone=seller.phone
        )
        db.add(store)
        db.commit()
        print("Sample store created successfully!")
    else:
        print("Sample store already exists")

    # Check if sample products exist
    products = db.query(Product).filter(Product.store_id == store.id).all()
    if not products:
        print("Creating sample products...")
        products = [
            Product(
                store_id=store.id,
                name="Sample Product 1",
                description="A high-quality sample product",
                price=99.99,
                stock_quantity=100,
                category="Electronics",
                status=ProductStatus.ACTIVE
            ),
            Product(
                store_id=store.id,
                name="Sample Product 2",
                description="Another amazing product",
                price=49.99,
                stock_quantity=50,
                category="Fashion",
                status=ProductStatus.ACTIVE
            )
        ]
        for product in products:
            db.add(product)
        db.commit()
        print("Sample products created successfully!")
    else:
        print("Sample products already exist")

    # Check if sample order exists
    order = db.query(Order).filter(
        Order.buyer_id == buyer.id,
        Order.store_id == store.id
    ).first()
    if not order:
        print("Creating sample order...")
        order = Order(
            buyer_id=buyer.id,
            store_id=store.id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            payment_method=PaymentMethod.CREDIT_CARD,
            shipping_address={
                "full_name": buyer.full_name,
                "address_line1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "US",
                "phone": buyer.phone
            },
            subtotal=99.99,
            shipping_cost=10.00,
            tax=11.00,
            total_amount=120.99,
            currency="USD"
        )
        db.add(order)
        db.commit()
        print("Sample order created successfully!")

        print("Creating order items...")
        order_item = OrderItem(
            order_id=order.id,
            product_id=products[0].id,
            quantity=1,
            unit_price=products[0].price,
            subtotal=products[0].price,
            product_name=products[0].name
        )
        db.add(order_item)
        db.commit()
        print("Order items created successfully!")
    else:
        print("Sample order already exists")

def main() -> None:
    print("Initializing database...")
    db = SessionLocal()
    try:
        init_db(db)
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
