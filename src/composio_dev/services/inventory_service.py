from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from models import InventoryItem, ReorderPlan, PriorityLevel, ForecastResult
from services.forecast_service import ForecastService
from services.composio_service import ComposioService
from database import crud


class InventoryService:
    def __init__(self, db: Session = None):
        self.forecast_service = ForecastService()
        self.composio_service = ComposioService()
        self.db = db  # Database session will be passed from endpoints
    
    def _inventory_item_from_db(self, product) -> InventoryItem:
        """Convert database Product model to InventoryItem Pydantic model."""
        return InventoryItem(
            item_id=product.item_id,
            name=product.name,
            current_stock=product.current_stock,
            min_threshold=product.min_threshold,
            daily_usage=product.daily_usage,
            supplier=product.supplier or "",
            unit_cost=product.unit_cost
        )
    
    async def sync_inventory(self, spreadsheet_id: str, db: Session) -> Dict[str, str]:
        try:
            items = await self.composio_service.sync_inventory_from_sheets(spreadsheet_id)
            
            # Store items in database using upsert
            synced_count = 0
            for item in items:
                crud.upsert_product(
                    db=db,
                    item_id=item.item_id,
                    name=item.name,
                    current_stock=item.current_stock,
                    min_threshold=item.min_threshold,
                    daily_usage=item.daily_usage,
                    supplier=item.supplier,
                    unit_cost=item.unit_cost,
                    sku=item.item_id
                )
                synced_count += 1
            
            return {
                "status": "success",
                "message": f"Synced {synced_count} items from Google Sheets",
                "items_count": synced_count
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to sync inventory: {str(e)}"
            }
    
    async def generate_forecasts(self, db: Session, forecast_days: int = 30) -> List[ForecastResult]:
        # Get all products from database
        db_products = crud.get_all_products(db)
        
        if not db_products:
            return []
        
        # Convert to InventoryItem models for forecast service
        items = [self._inventory_item_from_db(p) for p in db_products]
        
        forecasts = await self.forecast_service.forecast_depletion(items, forecast_days)
        return forecasts
    
    async def create_reorder_plans(self, forecasts: List[ForecastResult], 
                                   notion_database_id: str, db: Session) -> List[ReorderPlan]:
        plans = []
        
        for forecast in forecasts:
            # Get product from database
            product = crud.get_product_by_item_id(db, forecast.item_id)
            if not product:
                continue
            
            if forecast.days_until_depletion <= 14:
                # Convert to InventoryItem for calculation
                item = self._inventory_item_from_db(product)
                order_quantity = self.forecast_service.calculate_reorder_quantity(item)
                
                if forecast.days_until_depletion <= 7:
                    priority = PriorityLevel.HIGH
                elif forecast.days_until_depletion <= 14:
                    priority = PriorityLevel.MEDIUM
                else:
                    priority = PriorityLevel.LOW
                
                justification = f"Stock will deplete in {forecast.days_until_depletion} days. "
                justification += f"Risk factors: {', '.join(forecast.risk_factors)}. "
                justification += f"Confidence: {forecast.confidence_score:.1%}"
                
                plan = ReorderPlan(
                    item_id=item.item_id,
                    item_name=item.name,
                    current_stock=item.current_stock,
                    predicted_depletion_date=forecast.predicted_depletion_date,
                    recommended_order_quantity=order_quantity,
                    supplier=item.supplier,
                    estimated_cost=order_quantity * item.unit_cost,
                    priority=priority,
                    justification=justification
                )
                
                try:
                    # Create Notion page
                    notion_page_id = await self.composio_service.create_notion_reorder_plan(
                        notion_database_id, plan
                    )
                    
                    # Save reorder plan to database
                    crud.create_reorder_plan(
                        db=db,
                        product_id=product.id,
                        predicted_depletion_date=forecast.predicted_depletion_date,
                        recommended_order_quantity=order_quantity,
                        estimated_cost=order_quantity * item.unit_cost,
                        priority=priority.value,
                        justification=justification,
                        notion_page_id=notion_page_id
                    )
                    
                    plans.append(plan)
                
                except Exception as e:
                    print(f"Failed to create Notion plan for {item.name}: {str(e)}")
        
        return plans
    
    async def send_approval_requests(self, plans: List[ReorderPlan], 
                                    approver_email: str) -> Dict[str, str]:
        try:
            if not plans:
                return {"status": "info", "message": "No plans to approve"}
            
            high_priority = [p for p in plans if p.priority == PriorityLevel.HIGH]
            medium_priority = [p for p in plans if p.priority == PriorityLevel.MEDIUM]
            
            if high_priority:
                subject = f"URGENT: Inventory Reorder Approval - {len(high_priority)} Critical Items"
                body = "URGENT APPROVAL REQUIRED\n\nThe following items require immediate reorder approval:"
                
                await self.composio_service.send_approval_email(
                    approver_email, subject, body, high_priority
                )
            
            if medium_priority:
                subject = f"Inventory Reorder Approval - {len(medium_priority)} Items"
                body = "The following items require reorder approval:"
                
                await self.composio_service.send_approval_email(
                    approver_email, subject, body, medium_priority
                )
            
            total_cost = sum(plan.estimated_cost for plan in plans)
            
            return {
                "status": "success",
                "message": f"Approval requests sent for {len(plans)} items",
                "total_cost": total_cost,
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send approval requests: {str(e)}"
            }
    
    def get_inventory_summary(self, db: Session) -> Dict:
        products = crud.get_all_products(db)
        
        if not products:
            return {"total_items": 0, "total_value": 0}
        
        total_items = len(products)
        total_value = sum(p.current_stock * p.unit_cost for p in products)
        
        low_stock_count = sum(1 for p in products if p.current_stock <= p.min_threshold)
        
        pending_plans = crud.get_pending_reorder_plans(db)
        
        return {
            "total_items": total_items,
            "total_value": total_value,
            "low_stock_count": low_stock_count,
            "pending_reorders": len(pending_plans)
        }