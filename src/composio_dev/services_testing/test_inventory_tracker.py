import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from services.inventory_tracker import InventoryTracker
import asyncio

# Test configuration
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # Replace with actual ID
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # Replace with actual ID

async def test_inventory_tracking():
    """Test the complete inventory tracking workflow"""
    print("🧪 Testing Inventory Tracker...")
    
    # Initialize tracker
    tracker = InventoryTracker(SPREADSHEET_ID, NOTION_DATABASE_ID)
    
    # Test 1: Get current inventory status
    print("\n📊 Testing inventory status retrieval...")
    status = tracker.get_inventory_status()
    print(f"Inventory status: {status}")
    
    # Test 2: Sync and track low stock items
    print("\n🔄 Testing sync and track...")
    result = await tracker.sync_and_track()
    # print(f"Sync result: {result}")
    
    # Test 3: Update stock level (simulate stock change)
    print("\n📝 Testing stock update...")
    update_result = tracker.update_stock_level(3, 15)  # Update row 3 to 15 units
    # print(f"Update result: {update_result}")
    
    # Test 4: Get pending approvals
    print("\n📋 Testing pending approvals...")
    pending = tracker.get_pending_approvals()
    # print(f"Pending approvals: {pending}")

def test_services_individually():
    """Test individual services"""
    from services.sheets_service import SheetsService
    from services.notion_service import NotionService
    
    print("🧪 Testing individual services...")
    
    # Test Sheets Service
    sheets = SheetsService()
    print(f"Sheets connected: {sheets.connected}")
    
    # Test Notion Service  
    notion = NotionService()
    print(f"Notion connected: {notion.connected}")

if __name__ == "__main__":
    print("Choose test:")
    print("1. Test individual services")
    print("2. Test complete workflow")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        test_services_individually()
    elif choice == "2":
        if SPREADSHEET_ID == "your_google_sheets_id":
            print("❌ Please update SPREADSHEET_ID and NOTION_DATABASE_ID in the test file")
        else:
            asyncio.run(test_inventory_tracking())
    else:
        print("Invalid choice")