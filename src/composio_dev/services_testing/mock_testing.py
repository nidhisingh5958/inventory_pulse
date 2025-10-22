import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from helper.utils import toolset, gemini_draft_email
from config.redis_cofig import redis_client
import asyncio
import json


NEW_MOCK_DATA = {
    "email": "ABC@gmail.com",
    "new_stock_left": 50,
    "demand": 30,
    "supplier": "ABC Suppliers",
}

PREVIOUS_MOCK_DATA = {
    "email": "ABC@gmail.com",
    "stock_left": 100,
    "demand": 30,
    "supplier": "ABC Suppliers",
}

async def test_mock_data():
    print("Simulating DB update...")
    await asyncio.sleep(2)  # ✅ Non-blocking sleep
    print("DB update simulated... checking for low stock alert condition...")

    # Simulate stock reduction
    NEW_MOCK_DATA["new_stock_left"] = 20

    # ✅ Correct condition (alert only when stock decreases below previous value)
    if NEW_MOCK_DATA["new_stock_left"] < PREVIOUS_MOCK_DATA["stock_left"]:
        print("⚠️ Low stock detected! Publishing alert to Redis...")
        await redis_client.publish("low_stock_alerts", json.dumps(NEW_MOCK_DATA))
    else:
        print("✅ Stock level is sufficient. No alert sent.")




    
