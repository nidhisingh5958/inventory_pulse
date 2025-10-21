import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from services.sheets_service import SheetsService
from services.notion_service import NotionService
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_sheets_crud():
    """Test Google Sheets CRUD operations"""
    print_section("GOOGLE SHEETS CRUD OPERATIONS TEST")
    
    sheets = SheetsService()
    
    if not sheets.connected:
        print("❌ Google Sheets not connected")
        return
    
    # ===== READ Operations =====
    print("📖 READ OPERATIONS")
    print("-" * 40)
    
    # Read all items
    print("\n1️⃣  Reading all items...")
    all_items = sheets.get_all_items(SPREADSHEET_ID)
    print(f"✅ Found {all_items.get('total', 0)} items")
    if all_items.get("items"):
        for item in all_items["items"][:3]:  # Show first 3
            print(f"   - {item['item_id']}: {item['item_name']} (Stock: {item['current_stock']})")
    
    # Read specific item
    print("\n2️⃣  Reading specific item (ITEM001)...")
    item = sheets.get_row_by_id(SPREADSHEET_ID, "ITEM001")
    if item.get("error"):
        print(f"❌ {item['error']}")
    else:
        print(f"✅ Found: {item['item_name']}")
        print(f"   Current Stock: {item['current_stock']}")
        print(f"   Min Threshold: {item['min_threshold']}")
        print(f"   Supplier: {item['supplier']}")
    
    # ===== CREATE Operations =====
    print("\n\n✍️  CREATE OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Creating new item...")
    new_item = sheets.create_inventory_item(
        SPREADSHEET_ID,
        item_id="ITEM999",
        item_name="Test Product",
        current_stock=50,
        min_threshold=20,
        daily_usage=5.0,
        supplier="Test Supplier",
        unit_cost=15.0
    )
    if new_item.get("error"):
        print(f"❌ Error: {new_item['error']}")
    else:
        print(f"✅ Item created successfully")
    
    # ===== UPDATE Operations =====
    print("\n\n🔄 UPDATE OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Updating stock for ITEM001...")
    update_result = sheets.update_stock(SPREADSHEET_ID, 3, 100)
    if update_result.get("error"):
        print(f"❌ Error: {update_result['error']}")
    else:
        print(f"✅ Stock updated to 100")
    
    print("\n2️⃣  Updating item details...")
    update_item_result = sheets.update_item(
        SPREADSHEET_ID,
        "ITEM001",
        item_name="Updated Pens",
        min_threshold=15,
        daily_usage=3.0
    )
    if update_item_result.get("error"):
        print(f"❌ Error: {update_item_result['error']}")
    else:
        print(f"✅ Item updated successfully")
    
    # ===== DELETE Operations =====
    print("\n\n🗑️  DELETE OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Deleting test item (ITEM999)...")
    delete_result = sheets.delete_item(SPREADSHEET_ID, "ITEM999")
    if delete_result.get("error"):
        print(f"❌ Error: {delete_result['error']}")
    else:
        print(f"✅ Item deleted successfully")
    
    # ===== QUERY Operations =====
    print("\n\n🔍 QUERY OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Finding low stock items...")
    low_stock = sheets.track_stock_changes(SPREADSHEET_ID)
    if low_stock.get("error"):
        print(f"❌ Error: {low_stock['error']}")
    else:
        items = low_stock.get("low_stock_items", [])
        print(f"✅ Found {len(items)} low stock items")
        for item in items:
            print(f"   - {item['item_name']}: {item['current_stock']} / {item['min_threshold']}")

def test_notion_crud():
    """Test Notion CRUD operations"""
    print_section("NOTION DATABASE CRUD OPERATIONS TEST")
    
    notion = NotionService()
    
    if not notion.connected:
        print("❌ Notion not connected")
        return
    
    # ===== READ Operations =====
    print("📖 READ OPERATIONS")
    print("-" * 40)
    
    # Read all reorder plans
    print("\n1️⃣  Reading all reorder plans...")
    all_plans = notion.get_all_reorder_plans(NOTION_DATABASE_ID)
    if all_plans.get("error"):
        print(f"❌ Error: {all_plans['error']}")
    else:
        plans = all_plans.get("reorder_plans", [])
        print(f"✅ Found {len(plans)} reorder plans")
        for plan in plans[:3]:  # Show first 3
            print(f"   - {plan['item_name']}: {plan['status']} (Priority: {plan['priority']})")
    
    # Read pending orders
    print("\n2️⃣  Reading pending orders...")
    pending = notion.get_pending_orders(NOTION_DATABASE_ID)
    if pending.get("error"):
        print(f"❌ Error: {pending['error']}")
    else:
        orders = pending.get("pending_orders", [])
        print(f"✅ Found {len(orders)} pending orders")
        for order in orders[:2]:
            print(f"   - {order['item_name']}: {order['cost']} (Qty: {order['order_quantity']})")
    
    # ===== CREATE Operations =====
    print("\n\n✍️  CREATE OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Creating new reorder plan...")
    test_item = {
        "item_name": "Urgent Supplies",
        "current_stock": 2,
        "min_threshold": 20,
        "daily_usage": 3.0,
        "supplier": "Urgent Supplier",
        "unit_cost": 25.0
    }
    
    new_plan = notion.create_reorder_plan(NOTION_DATABASE_ID, test_item)
    if new_plan.get("error"):
        print(f"❌ Error: {new_plan['error']}")
    else:
        print(f"✅ Reorder plan created successfully")
        print(f"   Page ID: {new_plan.get('data', {}).get('response_data', {}).get('id', 'N/A')}")
    
    # ===== UPDATE Operations =====
    print("\n\n🔄 UPDATE OPERATIONS")
    print("-" * 40)
    
    # Get a pending order to update
    pending = notion.get_pending_orders(NOTION_DATABASE_ID)
    if pending.get("pending_orders") and len(pending["pending_orders"]) > 0:
        page_id = pending["pending_orders"][0]["page_id"]
        
        print(f"\n1️⃣  Updating order status to 'Approved'...")
        update_result = notion.update_reorder_status(page_id, "Approved")
        if update_result.get("error"):
            print(f"❌ Error: {update_result['error']}")
        else:
            print(f"✅ Status updated to 'Approved'")
        
        print(f"\n2️⃣  Updating order priority to 'Medium'...")
        update_result = notion.update_reorder_plan(page_id, Priority="Medium")
        if update_result.get("error"):
            print(f"❌ Error: {update_result['error']}")
        else:
            print(f"✅ Priority updated to 'Medium'")
    else:
        print("⚠️  No pending orders to update")
    
    # ===== DELETE Operations =====
    print("\n\n🗑️  DELETE OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Deleting reorder plan...")
    if pending.get("pending_orders") and len(pending["pending_orders"]) > 0:
        # Use the last one to delete
        page_id = pending["pending_orders"][-1]["page_id"]
        delete_result = notion.delete_reorder_plan(page_id)
        if delete_result.get("error"):
            print(f"❌ Error: {delete_result['error']}")
        else:
            print(f"✅ Reorder plan deleted successfully")
    else:
        print("⚠️  No plans available to delete")
    
    # ===== QUERY Operations =====
    print("\n\n🔍 QUERY OPERATIONS")
    print("-" * 40)
    
    print("\n1️⃣  Finding high priority orders...")
    high_priority = notion.get_high_priority_orders(NOTION_DATABASE_ID)
    if high_priority.get("error"):
        print(f"❌ Error: {high_priority['error']}")
    else:
        orders = high_priority.get("high_priority_orders", [])
        print(f"✅ Found {len(orders)} high priority orders")
        for order in orders:
            print(f"   - {order['item_name']}: {order['status']}")
    
    print("\n2️⃣  Finding approved orders...")
    approved = notion.get_reorders_by_status(NOTION_DATABASE_ID, "Approved")
    if approved.get("error"):
        print(f"❌ Error: {approved['error']}")
    else:
        orders = approved.get("reorder_plans", [])
        print(f"✅ Found {len(orders)} approved orders")
        for order in orders:
            print(f"   - {order['item_name']}: Cost ${order['cost']}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  CRUD OPERATIONS TEST SUITE")
    print("="*60)
    
    # Test Google Sheets
    test_sheets_crud()
    
    # Test Notion
    test_notion_crud()
    
    print_section("TEST COMPLETE ✅")
    print("All CRUD operations have been tested!")
