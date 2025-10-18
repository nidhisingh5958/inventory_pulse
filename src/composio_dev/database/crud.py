from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from . import models, schemas


# Product CRUD operations
def get_product_by_item_id(db: Session, item_id: str) -> Optional[models.Product]:
    """Get a product by its item_id."""
    return db.query(models.Product).filter(models.Product.item_id == item_id).first()


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    """Get a product by its database id."""
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """Get all products with pagination."""
    return db.query(models.Product).offset(skip).limit(limit).all()


def create_product(db: Session, item_id: str, name: str, current_stock: int, 
                   min_threshold: int, daily_usage: float, supplier: str, 
                   unit_cost: float, sku: Optional[str] = None) -> models.Product:
    """Create a new product."""
    db_product = models.Product(
        item_id=item_id,
        name=name,
        sku=sku or item_id,
        current_stock=current_stock,
        min_threshold=min_threshold,
        daily_usage=daily_usage,
        supplier=supplier,
        unit_cost=unit_cost
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product_stock(db: Session, product_id: int, new_stock: int, 
                         change: int, reason: Optional[str] = None) -> models.Product:
    """Update product stock and log the change."""
    product = get_product_by_id(db, product_id)
    if not product:
        raise ValueError(f"Product with id {product_id} not found")
    
    product.current_stock = new_stock
    product.last_updated = datetime.utcnow()
    
    # Create inventory log
    log = models.InventoryLog(
        product_id=product_id,
        change=change,
        reason=reason
    )
    db.add(log)
    db.commit()
    db.refresh(product)
    return product


def upsert_product(db: Session, item_id: str, name: str, current_stock: int,
                   min_threshold: int, daily_usage: float, supplier: str,
                   unit_cost: float, sku: Optional[str] = None) -> models.Product:
    """Create or update a product."""
    product = get_product_by_item_id(db, item_id)
    
    if product:
        # Update existing product
        old_stock = product.current_stock
        product.name = name
        product.current_stock = current_stock
        product.min_threshold = min_threshold
        product.daily_usage = daily_usage
        product.supplier = supplier
        product.unit_cost = unit_cost
        product.last_updated = datetime.utcnow()
        if sku:
            product.sku = sku
        
        # Log stock change if different
        if old_stock != current_stock:
            log = models.InventoryLog(
                product_id=product.id,
                change=current_stock - old_stock,
                reason="Sync from external source"
            )
            db.add(log)
        
        db.commit()
        db.refresh(product)
        return product
    else:
        # Create new product
        return create_product(db, item_id, name, current_stock, min_threshold,
                            daily_usage, supplier, unit_cost, sku)


def get_low_stock_products(db: Session) -> List[models.Product]:
    """Get products that are below their minimum threshold."""
    return db.query(models.Product).filter(
        models.Product.current_stock <= models.Product.min_threshold
    ).all()


# Inventory Log CRUD operations
def create_inventory_log(db: Session, product_id: int, change: int, 
                        reason: Optional[str] = None) -> models.InventoryLog:
    """Create an inventory log entry."""
    log = models.InventoryLog(
        product_id=product_id,
        change=change,
        reason=reason
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_product_logs(db: Session, product_id: int, limit: int = 50) -> List[models.InventoryLog]:
    """Get inventory logs for a specific product."""
    return db.query(models.InventoryLog).filter(
        models.InventoryLog.product_id == product_id
    ).order_by(models.InventoryLog.created_at.desc()).limit(limit).all()


# Reorder Plan CRUD operations
def create_reorder_plan(db: Session, product_id: int, predicted_depletion_date: str,
                       recommended_order_quantity: int, estimated_cost: float,
                       priority: str, justification: str,
                       notion_page_id: Optional[str] = None) -> models.ReorderPlan:
    """Create a reorder plan."""
    plan = models.ReorderPlan(
        product_id=product_id,
        predicted_depletion_date=predicted_depletion_date,
        recommended_order_quantity=recommended_order_quantity,
        estimated_cost=estimated_cost,
        priority=priority,
        justification=justification,
        notion_page_id=notion_page_id
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_pending_reorder_plans(db: Session) -> List[models.ReorderPlan]:
    """Get all pending reorder plans."""
    return db.query(models.ReorderPlan).filter(
        models.ReorderPlan.status == "pending"
    ).all()


def update_reorder_plan_status(db: Session, plan_id: int, status: str) -> models.ReorderPlan:
    """Update the status of a reorder plan."""
    plan = db.query(models.ReorderPlan).filter(models.ReorderPlan.id == plan_id).first()
    if not plan:
        raise ValueError(f"Reorder plan with id {plan_id} not found")
    
    plan.status = status
    db.commit()
    db.refresh(plan)
    return plan


def get_reorder_plans_for_product(db: Session, product_id: int) -> List[models.ReorderPlan]:
    """Get all reorder plans for a specific product."""
    return db.query(models.ReorderPlan).filter(
        models.ReorderPlan.product_id == product_id
    ).order_by(models.ReorderPlan.created_at.desc()).all()


# Integration CRUD operations
def create_integration(db: Session, user_id: str, app_name: str,
                      access_token: str, refresh_token: Optional[str] = None,
                      metadata: Optional[dict] = None) -> models.Integration:
    """Create an integration."""
    integration = models.Integration(
        user_id=user_id,
        app_name=app_name,
        access_token=access_token,
        refresh_token=refresh_token,
        metadata=metadata or {}
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def get_active_integrations(db: Session, user_id: str) -> List[models.Integration]:
    """Get all active integrations for a user."""
    return db.query(models.Integration).filter(
        models.Integration.user_id == user_id,
        models.Integration.active == True
    ).all()
