import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from composio_dev.helper.utils import toolset, gemini_draft_email
from composio_dev.config.redis_cofig import redis_client
import asyncio
import json
import traceback
from composio_dev.services_testing.mock_testing import test_mock_data
from composio_dev.helper.utils import convert_string_to_json
# from composio_dev.services.inventory_service import InventoryService

load_dotenv()

app = FastAPI(
    title="Inventory Replenishment Copilot",
    version="1.0.0",
    description="AI-powered inventory management with Google Sheets, Notion, and Gmail integration"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ✅ Global task reference
listener_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background listener when app starts"""
    global listener_task
    print("🚀 Starting Redis listener...")
    # subscribe to Redis channels first, before publishing any messages
    listener_task = asyncio.create_task(redis_listener())
    yield
    # Cleanup on shutdown
    if listener_task:
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            print("✅ Redis listener stopped")

# ✅ Update your FastAPI app initialization
app = FastAPI(lifespan=lifespan)

# ✅ Background listener function
async def redis_listener():
    """Continuously listen for Redis messages"""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("low_stock_alerts")
    print("✅ Subscribed to low_stock_alerts channel...")

    while True:
        try:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)

            if msg is None:
                await asyncio.sleep(0.1)  # Prevent CPU spinning
                continue

            print(f"📥 Raw Redis message: {msg}")
            alert_data = json.loads(msg["data"])
            print(f"Parsed Alert Data: {alert_data}")

            print("✉️ Invoking Gemini draft email function...")
            res = gemini_draft_email(
                recipient_email=alert_data["email"],
                context=(
                    f"I am running low on stocks, draft an email to my supplier {alert_data['supplier']}.\n"
                    f"Current stock left: {alert_data['new_stock_left']} units, "
                    f"Daily demand: {alert_data['demand']} units. "
                    "Request to replenish as soon as possible."
                )
            )
            print(f"Draft email: {res}")
            json_res = convert_string_to_json(res)
            print("type of json_res:", type(json_res))

            if json_res is None:
                print("❌ AI response is not valid JSON, skipping email send.")
                return {"status": "error", "message": "AI response is not valid JSON."}

            try:
                print("📨 Sending email via Composio...")
                result = toolset.execute_action(
                    action="GMAIL_SEND_EMAIL",
                    params={
                        "recipient_email": json_res['recipient_email'],
                        "subject": json_res['subject'],
                        "body": json_res['body']
                    }
                )
                print("✅ Email sent successfully!")

            except Exception as e:
                print(f"❌ Error while sending email: {e}")
                traceback.print_exc()

        except asyncio.CancelledError:
            print("❗ Listener task cancelled.")
            break
        except Exception as e:
            print(f"❌ Error in listener: {e}")
            traceback.print_exc()
            await asyncio.sleep(1)  # Wait before retrying

# ✅ Simplified endpoint - just triggers the alert
@app.post("/simulate_low_stock_alert/")
async def simulate_low_stock_alert():
    """Trigger a low stock alert simulation"""
    await test_mock_data()
    return {
        "status": "success", 
        "message": "Low stock alert triggered. Check logs for email sending status."
    }





# # Initialize service
# inventory_service = InventoryService()

# # Configuration
# SPREADSHEET_ID = "your_google_sheets_id"
# NOTION_DATABASE_ID = "your_notion_database_id"
# APPROVER_EMAIL = "manager@company.com"

# @app.get("/")
# async def root():
#     return {
#         "message": "Inventory Replenishment Copilot API",
#         "version": "1.0.0",
#         "features": [
#             "Google Sheets inventory tracking",
#             "Groq AI-powered depletion forecasting",
#             "Notion reorder plan management",
#             "Gmail approval notifications"
#         ]
#     }

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "Inventory Replenishment Copilot"}

# @app.post("/inventory/sync")
# async def sync_inventory():
#     result = await inventory_service.sync_inventory(SPREADSHEET_ID)
#     if result["status"] == "error":
#         raise HTTPException(status_code=500, detail=result["message"])
#     return result

# @app.get("/inventory/status")
# async def get_inventory_status():
#     return inventory_service.get_inventory_summary()

# @app.post("/forecast/generate")
# async def generate_forecasts(forecast_days: int = 30):
#     try:
#         forecasts = await inventory_service.generate_forecasts(forecast_days)
#         return {"forecasts": forecasts, "count": len(forecasts)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

# @app.post("/reorder/create-plans")
# async def create_reorder_plans(forecast_days: int = 30):
#     try:
#         forecasts = await inventory_service.generate_forecasts(forecast_days)
#         plans = await inventory_service.create_reorder_plans(forecasts, NOTION_DATABASE_ID)
        
#         return {
#             "message": f"Created {len(plans)} reorder plans",
#             "plans": plans,
#             "total_cost": sum(plan.estimated_cost for plan in plans)
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create reorder plans: {str(e)}")

# @app.post("/approval/send")
# async def send_approval_requests():
#     try:
#         pending_plans = []
#         for plan_data in inventory_service.reorder_plans.values():
#             if plan_data["status"] == "pending":
#                 pending_plans.append(plan_data["plan"])
        
#         if not pending_plans:
#             return {"message": "No pending plans to approve"}
        
#         result = await inventory_service.send_approval_requests(pending_plans, APPROVER_EMAIL)
        
#         if result["status"] == "error":
#             raise HTTPException(status_code=500, detail=result["message"])
        
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send approval requests: {str(e)}")

# @app.post("/workflow/auto-replenishment")
# async def run_auto_replenishment_workflow():
#     try:
#         # Step 1: Sync inventory
#         sync_result = await inventory_service.sync_inventory(SPREADSHEET_ID)
#         if sync_result["status"] == "error":
#             raise HTTPException(status_code=500, detail=sync_result["message"])
        
#         # Step 2: Generate forecasts
#         forecasts = await inventory_service.generate_forecasts(30)
        
#         # Step 3: Create reorder plans
#         plans = await inventory_service.create_reorder_plans(forecasts, NOTION_DATABASE_ID)
        
#         # Step 4: Send approval requests for high priority items
#         high_priority_plans = [p for p in plans if p.priority.value == "High"]
        
#         approval_result = {"message": "No high priority items"}
#         if high_priority_plans:
#             approval_result = await inventory_service.send_approval_requests(
#                 high_priority_plans, APPROVER_EMAIL
#             )
        
#         return {
#             "workflow_status": "completed",
#             "items_synced": sync_result.get("items_count", 0),
#             "forecasts_generated": len(forecasts),
#             "plans_created": len(plans),
#             "high_priority_plans": len(high_priority_plans),
#             "approval_result": approval_result,
#             "total_estimated_cost": sum(plan.estimated_cost for plan in plans)
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

# @app.get("/reorder/plans")
# async def get_reorder_plans():
#     plans_data = []
#     for item_id, plan_data in inventory_service.reorder_plans.items():
#         plans_data.append({
#             "item_id": item_id,
#             "plan": plan_data["plan"],
#             "status": plan_data["status"],
#             "notion_page_id": plan_data.get("notion_page_id"),
#             "created_at": plan_data.get("created_at")
#         })
    
#     return {"plans": plans_data, "count": len(plans_data)}

# @app.post("/config/update")
# async def update_configuration(config: Dict[str, str]):
#     global SPREADSHEET_ID, NOTION_DATABASE_ID, APPROVER_EMAIL
    
#     if "spreadsheet_id" in config:
#         SPREADSHEET_ID = config["spreadsheet_id"]
    
#     if "notion_database_id" in config:
#         NOTION_DATABASE_ID = config["notion_database_id"]
    
#     if "approver_email" in config:
#         APPROVER_EMAIL = config["approver_email"]
    
#     return {
#         "message": "Configuration updated",
#         "current_config": {
#             "spreadsheet_id": SPREADSHEET_ID,
#             "notion_database_id": NOTION_DATABASE_ID,
#             "approver_email": APPROVER_EMAIL
#         }
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)