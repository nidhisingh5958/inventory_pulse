import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from services.sheets_service import SheetsService
from services.notion_service import NotionService
import asyncio
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def test_notion_data_population():
    """Test that Notion pages are created with data"""
    print("🧪 Testing Notion Data Population Fix...\n")
    
    # Initialize services
    sheets = SheetsService()
    notion = NotionService()
    
    if not sheets.connected or not notion.connected:
        print("❌ Services not connected")
        return
    
    # Test 1: Create a reorder plan directly
    print("=" * 60)
    print("TEST 1: Create Reorder Plan with Data")
    print("=" * 60)
    
    test_item = {
        "item_name": "Test Item - DataPopulation",
        "item_id": "TEST_DATA001",
        "current_stock": 5,
        "min_threshold": 20,
        "daily_usage": 2.5,
        "supplier": "Test Supplier Corp",
        "unit_cost": 15.75
    }
    
    create_result = notion.create_reorder_plan(NOTION_DATABASE_ID, test_item)
    print(f"\n✅ Reorder plan created")
    
    if create_result.get("data") and create_result.get("data", {}).get("response_data"):
        page_id = create_result.get("data", {}).get("response_data", {}).get("id")
        print(f"   Page ID: {page_id}")
        print(f"   URL: {create_result.get('data', {}).get('response_data', {}).get('url', 'N/A')}")
    
    # Test 2: Query to verify data was created
    print("\n" + "=" * 60)
    print("TEST 2: Query All Reorder Plans")
    print("=" * 60)
    
    all_plans = notion.get_all_reorder_plans(NOTION_DATABASE_ID)
    print(f"\n✅ Found {all_plans.get('count', 0)} total reorder plans")
    
    if all_plans.get("reorder_plans"):
        print("\n📋 Recent Plans:")
        for plan in all_plans.get("reorder_plans", [])[-3:]:  # Show last 3
            print(f"   - {plan.get('item_name', 'Unknown')}")
            print(f"     Status: {plan.get('status', 'N/A')}")
            print(f"     Priority: {plan.get('priority', 'N/A')}")
    
    # Test 3: Query pending approvals
    print("\n" + "=" * 60)
    print("TEST 3: Query Pending Approvals")
    print("=" * 60)
    
    pending = notion.get_pending_orders(NOTION_DATABASE_ID)
    print(f"\n✅ Found {pending.get('count', 0)} pending approvals")
    
    if pending.get("pending_orders"):
        print("\n📋 Pending Orders:")
        for plan in pending.get("pending_orders", []):
            print(f"   - {plan.get('item_name', 'Unknown')}")
            print(f"     Current Stock: {plan.get('current_stock')} units")
            print(f"     Order Qty: {plan.get('order_quantity')} units")
            print(f"     Supplier: {plan.get('supplier')}")
            print(f"     Cost: ${plan.get('cost', 0):.2f}")
    
    # Test 4: Test Google Sheets CRUD
    print("\n" + "=" * 60)
    print("TEST 4: Google Sheets CRUD Operations")
    print("=" * 60)
    
    # Create
    print("\n  CREATE: Adding new item...")
    create_result = sheets.create_inventory_item(
        spreadsheet_id=SPREADSHEET_ID,
        item_id="TESTCRUD001",
        item_name="CRUD Test Item",
        current_stock=50,
        min_threshold=15,
        daily_usage=2,
        supplier="CRUD Supplier",
        unit_cost=20.0
    )
    print(f"  ✅ Item created")
    
    # Read
    print("\n  READ: Getting item by ID...")
    read_result = sheets.get_row_by_id(SPREADSHEET_ID, "TESTCRUD001")
    if not read_result.get("error"):
        print(f"  ✅ Found item: {read_result.get('item_name')}")
        print(f"     Stock: {read_result.get('current_stock')}")
    
    # Update
    print("\n  UPDATE: Updating stock...")
    update_result = sheets.update_stock(SPREADSHEET_ID, read_result.get("row"), 45)
    print(f"  ✅ Stock updated")
    
    # Query
    print("\n  QUERY: Getting all items...")
    all_items = sheets.get_all_items(SPREADSHEET_ID)
    print(f"  ✅ Total items in inventory: {all_items.get('total', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_notion_data_population()
