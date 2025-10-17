from typing import List, Dict
from datetime import datetime
from models import InventoryItem, ReorderPlan, PriorityLevel, ForecastResult
from services.forecast_service import ForecastService
from services.composio_service import ComposioService

class InventoryService:
    def __init__(self):
        self.forecast_service = ForecastService()
        self.composio_service = ComposioService()
        self.inventory_data: Dict[str, InventoryItem] = {}
        self.reorder_plans: Dict[str, Dict] = {}
    
    async def sync_inventory(self, spreadsheet_id: str) -> Dict[str, str]:
        try:
            items = await self.composio_service.sync_inventory_from_sheets(spreadsheet_id)
            
            for item in items:
                self.inventory_data[item.item_id] = item
            
            return {
                "status": "success",
                "message": f"Synced {len(items)} items from Google Sheets",
                "items_count": len(items)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to sync inventory: {str(e)}"
            }
    
    async def generate_forecasts(self, forecast_days: int = 30) -> List[ForecastResult]:
        items = list(self.inventory_data.values())
        if not items:
            return []
        
        forecasts = await self.forecast_service.forecast_depletion(items, forecast_days)
        return forecasts
    
    async def create_reorder_plans(self, forecasts: List[ForecastResult], notion_database_id: str) -> List[ReorderPlan]:
        plans = []
        
        for forecast in forecasts:
            item = self.inventory_data.get(forecast.item_id)
            if not item:
                continue
            
            if forecast.days_until_depletion <= 14:
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
                    notion_page_id = await self.composio_service.create_notion_reorder_plan(
                        notion_database_id, plan
                    )
                    
                    self.reorder_plans[item.item_id] = {
                        "plan": plan,
                        "notion_page_id": notion_page_id,
                        "status": "pending",
                        "created_at": datetime.now()
                    }
                    
                    plans.append(plan)
                
                except Exception as e:
                    print(f"Failed to create Notion plan for {item.name}: {str(e)}")
        
        return plans
    
    async def send_approval_requests(self, plans: List[ReorderPlan], approver_email: str) -> Dict[str, str]:
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
    
    def get_inventory_summary(self) -> Dict:
        if not self.inventory_data:
            return {"total_items": 0, "total_value": 0}
        
        total_items = len(self.inventory_data)
        total_value = sum(item.current_stock * item.unit_cost for item in self.inventory_data.values())
        
        low_stock_count = sum(1 for item in self.inventory_data.values() 
                             if item.current_stock <= item.min_threshold)
        
        return {
            "total_items": total_items,
            "total_value": total_value,
            "low_stock_count": low_stock_count,
            "pending_reorders": len([p for p in self.reorder_plans.values() if p["status"] == "pending"])
        }