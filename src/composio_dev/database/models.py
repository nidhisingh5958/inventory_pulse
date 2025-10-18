from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db_config import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True)
    current_stock = Column(Integer, nullable=False)
    min_threshold = Column(Integer, nullable=False)
    supplier = Column(String, nullable=True)  # For supplier name/email
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    daily_usage = Column(Float, default=0.0)
    unit_cost = Column(Float, nullable=False, default=0.0)

    logs = relationship("InventoryLog", back_populates="product", cascade="all, delete-orphan")
    plans = relationship("ReorderPlan", back_populates="product", cascade="all, delete-orphan")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    change = Column(Integer, nullable=False)  # positive = restock, negative = sale
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="logs")


class ReorderPlan(Base):
    __tablename__ = "reorder_plans"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    predicted_depletion_date = Column(String, nullable=True)       
    recommended_order_quantity = Column(Integer, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    priority = Column(String, nullable=False)  # High, Medium, Low
    justification = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, approved, ordered
    notion_page_id = Column(String, nullable=True)  # For Notion integration tracking
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="plans")

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    app_name = Column(String)  # "google_sheets", "notion", "gmail"
    access_token = Column(String)
    refresh_token = Column(String, nullable=True)
    metadata = Column(JSON)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
