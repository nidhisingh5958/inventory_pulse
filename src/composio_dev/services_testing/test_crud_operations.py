import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from services.sheets_service import SheetsService
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
    all_items = sheets.get_inventory_data(SPREADSHEET_ID)
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
    new_item = sheets.create_new_stock_entry(
        SPREADSHEET_ID,
        {
            "item_id": "ITEM999",
            "item_name": "Test Product",
            "current_stock": 50,
            "min_threshold": 20,
            "daily_usage": 5.0,
            "supplier": "Test Supplier",
            "unit_cost": 15.0
        }
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
    update_item_result = sheets.update_stock(
        SPREADSHEET_ID,3 , 80,)
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

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  CRUD OPERATIONS TEST SUITE")
    print("="*60)
    
    # Test Google Sheets
    test_sheets_crud()
    
    print_section("TEST COMPLETE ✅")
    print("All CRUD operations have been tested!")
