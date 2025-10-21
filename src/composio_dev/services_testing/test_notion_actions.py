import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from services.notion_service import NotionService
from dotenv import load_dotenv

load_dotenv()

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def test_notion_operations():
    """Test Notion operations directly"""
    print("🧪 Testing Notion Service...")
    
    # Initialize Notion service
    notion = NotionService()
    print(f"Notion connected: {notion.connected}")
    
    if not notion.connected:
        print("❌ Notion not connected")
        return
    
    # Test 1: Query pending approvals
    print("\n📋 Testing query pending approvals...")
    pending = notion.get_pending_orders(NOTION_DATABASE_ID)
    print(f"Pending result: {pending}")
    
    # Test 2: Create a test reorder plan
    print("\n📝 Testing create reorder plan...")
    test_item = {
        "item_name": "Test Item",
        "item_id": "TEST001",
        "current_stock": 5,
        "min_threshold": 20,
        "daily_usage": 2,
        "supplier": "Test Supplier",
        "unit_cost": 10.0
    }
    
    result = notion.create_reorder_plan(NOTION_DATABASE_ID, test_item)
    print(f"Create result: {result}")
    
    # Test 3: Query again to see if it was created
    if result.get("error") is None:
        print("\n📋 Querying pending approvals again...")
        pending = notion.get_pending_orders(NOTION_DATABASE_ID)
        print(f"Pending result after create: {pending}")

if __name__ == "__main__":
    test_notion_operations()
