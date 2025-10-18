"""
Database package for Inventory Pulse application.

This package provides database configuration, models, and schemas
for managing inventory, reorder plans, and integrations.
"""

# Database configuration and session management
from .db_config import (
    Base,
    engine,
    SessionLocal,
    DATABASE_URL
)

# SQLAlchemy ORM Models
from .models import (
    Product,
    InventoryLog,
    ReorderPlan,
    Integration
)

# Pydantic schemas for validation
from .schemas import (
    ProductBase,
    ProductCreate,
    ProductResponse,
    InventoryLogCreate,
    ReorderPlanCreate,
    IntegrationCreate
)

# CRUD operations
from . import crud


# Database session dependency for FastAPI
def get_db():
    """
    Dependency function to get database session.
    Usage in FastAPI:
        @app.get("/products")
        def read_products(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database tables
def init_db():
    """
    Initialize database by creating all tables.
    Call this function when starting the application.
    """
    Base.metadata.create_all(bind=engine)


# Export all public components
__all__ = [
    # Database config
    "Base",
    "engine",
    "SessionLocal",
    "DATABASE_URL",
    "get_db",
    "init_db",
    
    # ORM Models
    "Product",
    "InventoryLog",
    "ReorderPlan",
    "Integration",
    
    # Pydantic Schemas
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "InventoryLogCreate",
    "ReorderPlanCreate",
    "IntegrationCreate",
    
    # CRUD operations
    "crud",
]
