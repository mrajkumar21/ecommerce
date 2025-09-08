# db.py
import os
from sqlalchemy import (
    create_engine, Column, Integer, String, DECIMAL, Text,
    ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import (
    scoped_session, sessionmaker, relationship, declarative_base
)
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy.engine import URL

# --------------------
# Load environment variables from .env
# --------------------
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "ecommerce_db")

if not all([DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError("Database configuration is missing in .env file")

# --------------------
# Engine & Session
# --------------------
url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASS,  # raw password
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(url, pool_pre_ping=True, echo=False)

db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )
)

Base = declarative_base()
Base.query = db_session.query_property()


# --------------------
# MODELS
# --------------------
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)  # ✅ now optional
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    total_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    status = Column(String(32), nullable=False, default='PLACED')
    created_at = Column(TIMESTAMP, server_default=func.now())
    items = relationship("OrderItem", cascade="all, delete-orphan", backref="order")


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    line_total = Column(DECIMAL(12, 2), nullable=False)


# --------------------
# DB SETUP & SESSION
# --------------------
def init_db():
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    session = db_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# --------------------
# PRODUCT HELPERS
# --------------------
def create_product(name, price, stock=0, description=None):
    with session_scope() as s:
        p = Product(
            # sku=sku if sku else None,
            name=name,
            price=Decimal(price),
            stock=int(stock),
            description=description
        )
        s.add(p)
        try:
            s.flush()
        except IntegrityError:
            s.rollback()
            raise


def update_product(product_id, **fields):
    with session_scope() as s:
        p = s.get(Product, product_id)
        if not p:
            raise ValueError("Product not found")
        for k, v in fields.items():
            if hasattr(p, k):
                setattr(p, k, v)
        s.add(p)


def delete_product(product_id):
    with session_scope() as s:
        p = s.get(Product, product_id)
        if not p:
            raise ValueError("Product not found")
        s.delete(p)


def list_products():
    with session_scope() as s:
        return s.query(Product).order_by(Product.id).all()


def adjust_stock(product_id, delta):
    with session_scope() as s:
        p = s.get(Product, product_id)
        if not p:
            raise ValueError("Product not found")
        new_stock = p.stock + int(delta)
        if new_stock < 0:
            raise ValueError("Insufficient stock")
        p.stock = new_stock
        s.add(p)


# --------------------
# ORDER HELPERS
# --------------------
def place_order(customer_name, customer_email, items):
    with session_scope() as s:
        order = Order(
            customer_name=customer_name,
            customer_email=customer_email,
            total_amount=0
        )
        s.add(order)
        s.flush()

        total = Decimal('0.00')
        for it in items:
            prod = s.get(Product, int(it['product_id']))
            if not prod:
                raise ValueError(f"Product id {it['product_id']} not found")
            qty = int(it['qty'])
            if qty <= 0:
                raise ValueError("Quantity must be > 0")
            if prod.stock < qty:
                raise ValueError(f"Insufficient stock for {prod.name} (available {prod.stock})")

            line_total = Decimal(prod.price) * qty
            order_item = OrderItem(
                order_id=order.id,
                product_id=prod.id,
                qty=qty,
                unit_price=prod.price,
                line_total=line_total
            )
            s.add(order_item)
            prod.stock -= qty
            s.add(prod)
            total += line_total

        order.total_amount = total
        s.add(order)
        s.flush()
        return order.id


def get_order(order_id):
    with session_scope() as s:
        return s.get(Order, order_id)


def list_orders():
    with session_scope() as s:
        return s.query(Order).order_by(Order.created_at.desc()).all()
