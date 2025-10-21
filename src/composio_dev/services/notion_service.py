import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from helper.utils import toolset
from composio import App
from datetime import datetime, timedelta
import json

class NotionService:
    def __init__(self):
        self.toolset = toolset
        self.connected = False
        self._check_connection()
    
    def _check_connection(self):
        """Check if Notion is connected"""
        try:
            accounts = self.toolset.get_connected_accounts()
            # If we have any connected accounts, assume Notion is available
            # since we're using the toolset which manages multiple integrations
            if accounts and len(accounts) > 0:
                self.connected = True
            else:
                self.connected = False
        except Exception as e:
            print(f"Error checking Notion connection: {e}")
            self.connected = False
    
    def create_reorder_plan(self, database_id: str, item_data: dict):
        """Create a reorder plan in Notion database"""
        if not self.connected:
            return {"error": "Notion not connected"}
        
        # Calculate depletion date and order quantity
        daily_usage = item_data.get("daily_usage", 1)
        current_stock = item_data.get("current_stock", 0)
        min_threshold = item_data.get("min_threshold", 0)
        
        days_until_depletion = max(0, (current_stock - min_threshold) / daily_usage)
        depletion_date = datetime.now() + timedelta(days=days_until_depletion)
        
        # Calculate order quantity (2x min threshold as safety stock)
        order_quantity = max(min_threshold * 2, 50)
        
        # Determine priority based on days until depletion
        if days_until_depletion <= 3:
            priority = "High"
        elif days_until_depletion <= 7:
            priority = "Medium"
        else:
            priority = "Low"
        
        try:
            result = self.toolset.execute_action(
                action="NOTION_UPDATE_PAGE",
                params={
                    "pageId": database_id,
                    "properties": {
                        "Item": {
                            "title": [{"text": {"content": item_data.get("item_name", "Unknown Item")}}]
                        },
                        "Current Stock": {
                            "number": current_stock
                        },
                        "Depletion Date": {
                            "date": {"start": depletion_date.strftime("%Y-%m-%d")}
                        },
                        "Order Quantity": {
                            "number": order_quantity
                        },
                        "Supplier": {
                            "richText": [{"text": {"content": item_data.get("supplier", "")}}]
                        },
                        "Cost": {
                            "number": float(item_data.get("unit_cost", 0)) * order_quantity
                        },
                        "Priority": {
                            "select": {"name": priority}
                        },
                        "Status": {
                            "select": {"name": "Pending Approval"}
                        }
                    }
                }
            )
            return result
        except Exception as e:
            return {"error": f"Failed to create reorder plan: {str(e)}"}
    
    def update_reorder_status(self, page_id: str, status: str):
        """Update the status of a reorder plan"""
        if not self.connected:
            return {"error": "Notion not connected"}
        
        try:
            result = self.toolset.execute_action(
                action="NOTION_UPDATE_PAGE",
                params={
                    "page_id": page_id,
                    "properties": {
                        "Status": {
                            "select": {"name": status}
                        }
                    }
                }
            )
            return result
        except Exception as e:
            return {"error": f"Failed to update status: {str(e)}"}
    
    def get_pending_orders(self, database_id: str):
        """Get all pending reorder plans"""
        if not self.connected:
            return {"error": "Notion not connected"}
        
        try:
            result = self.toolset.execute_action(
                action="NOTION_QUERY_DATABASE",
                params={
                    "database_id": database_id,
                    "filter": {
                        "property": "Status",
                        "select": {
                            "equals": "Pending Approval"
                        }
                    }
                }
            )
            return result
        except Exception as e:
            return {"error": f"Failed to query database: {str(e)}"}
    
    def bulk_create_reorder_plans(self, database_id: str, items_list: list):
        """Create multiple reorder plans at once"""
        results = []
        for item in items_list:
            result = self.create_reorder_plan(database_id, item)
            results.append({
                "item_name": item.get("item_name"),
                "result": result
            })
        return {"bulk_results": results}