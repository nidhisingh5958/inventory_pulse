from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from services.sheets_service import SheetsService
from services.notion_service import NotionService
from config.redis_cofig import redis_client
import json
import asyncio

class InventoryTracker:
    def __init__(self, spreadsheet_id: str, notion_database_id: str):
        self.sheets_service = SheetsService()
        self.notion_service = NotionService()
        self.spreadsheet_id = spreadsheet_id
        self.notion_database_id = notion_database_id
    
    async def sync_and_track(self):
        """Main method to sync inventory and create reorder plans"""
        print("🔄 Starting inventory sync and tracking...")
        
        # Get low stock items from Sheets
        low_stock_data = self.sheets_service.track_stock_changes(self.spreadsheet_id)
        
        if "error" in low_stock_data:
            print(f"❌ Error getting inventory data: {low_stock_data['error']}")
            return {"error": low_stock_data["error"]}
        
        low_stock_items = low_stock_data.get("low_stock_items", [])
        
        if not low_stock_items:
            print("✅ No low stock items found")
            return {"message": "No low stock items found"}
        
        print(f"⚠️ Found {len(low_stock_items)} low stock items")

        
        # Create reorder plans in Notion
        reorder_results = []
        for item in low_stock_items:
            # Add daily_usage calculation (using min_threshold/7 as estimate)
            item["daily_usage"] = max(1, item["min_threshold"] / 7)
            
            result = self.notion_service.create_reorder_plan(
                self.notion_database_id, 
                item
            )
            reorder_results.append({
                "item": item["item_name"],
                "result": result
            })
            
            # Publish alert to Redis
            alert_data = {
                "item_name": item["item_name"],
                "new_stock_left": item["current_stock"],
                "demand": 100,
                "supplier": 'Nidhi Singh',  # Placeholder supplier name
                "email": 'nidhisingh5958@gmail.com'  # Placeholder supplier email
            }
            await redis_client.publish("low_stock_alerts", json.dumps(alert_data))
        
        return {
            "low_stock_items": low_stock_items,
            "reorder_plans_created": reorder_results
        }
    
    def update_stock_level(self, item_row: int, new_stock: int):
        """Update stock level for specific item"""
        result = self.sheets_service.update_stock(self.spreadsheet_id, item_row, new_stock)
        return result

    def create_new_stock_entry(self, item_data: dict):
        """Create a new stock entry in the inventory sheet"""
        result = self.sheets_service.create_new_stock_entry(self.spreadsheet_id, item_data)
        return result

    def get_inventory_status(self):
        """Get current inventory status"""
        return self.sheets_service.get_inventory_data(self.spreadsheet_id)
    
    def get_pending_approvals(self):
        """Get pending reorder plans from Notion"""
        return self.notion_service.get_pending_orders(self.notion_database_id)
    
    def approve_reorder(self, page_id: str):
        """Approve a reorder plan"""
        return self.notion_service.update_reorder_status(page_id, "Approved")
    
    def reject_reorder(self, page_id: str):
        """Reject a reorder plan"""
        return self.notion_service.update_reorder_status(page_id, "Rejected")