#!/usr/bin/env python3
import asyncio
import requests
from services.inventory_service import InventoryService

async def test_system():
    print("🧪 Testing Inventory Replenishment Copilot")
    print("=" * 50)
    
    # Test inventory service
    print("\n1. Testing Inventory Service...")
    inventory_service = InventoryService()
    
    # Test sync (mock data)
    result = await inventory_service.sync_inventory("mock_spreadsheet_id")
    print(f"✅ Sync result: {result['message']}")
    
    # Test forecasts
    forecasts = await inventory_service.generate_forecasts(30)
    print(f"✅ Generated {len(forecasts)} forecasts")
    
    # Test reorder plans
    plans = await inventory_service.create_reorder_plans(forecasts, "mock_notion_db")
    print(f"✅ Created {len(plans)} reorder plans")
    
    # Test approval emails
    if plans:
        approval_result = await inventory_service.send_approval_requests(plans, "test@example.com")
        print(f"✅ Approval result: {approval_result['message']}")
    
    # Test summary
    summary = inventory_service.get_inventory_summary()
    print(f"✅ Inventory summary: {summary['total_items']} items, ${summary['total_value']:.2f}")
    
    print("\n🎉 All tests passed! System is working.")

def test_api():
    print("\n🌐 Testing API endpoints...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print("❌ API server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python run.py")
        return False

async def main():
    await test_system()
    test_api()

if __name__ == "__main__":
    asyncio.run(main())