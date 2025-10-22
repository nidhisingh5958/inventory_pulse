import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from composio_dev.helper.utils import redis_listener
import asyncio
from composio_dev.services_testing.mock_testing import test_mock_data
from composio_dev.services.inventory_tracker import InventoryTracker as InventoryService
from scalar_fastapi import get_scalar_api_reference

load_dotenv()

# Configuration
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or "your_spreadsheet_id"
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID") or "your_notion_database_id"
APPROVER_EMAIL = os.getenv("APPROVER_EMAIL") or "manager@company.com"

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

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )

# ✅ Simplified endpoint - just triggers the alert
@app.post("/simulate_low_stock_alert/")
async def simulate_low_stock_alert():
    """Trigger a low stock alert simulation"""
    await test_mock_data()
    return {
        "status": "success", 
        "message": "Low stock alert triggered. Check logs for email sending status."
    }

# Initialize service
inventory_service = InventoryService(SPREADSHEET_ID, NOTION_DATABASE_ID)


@app.get("/")
async def root():
    return {
        "message": "Inventory Replenishment Copilot API",
        "version": "1.0.0",
        "features": [
            "Google Sheets inventory tracking",
            "Groq AI-powered depletion forecasting",
            "Notion reorder plan management",
            "Gmail approval notifications"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Inventory Replenishment Copilot"}

@app.post("/inventory/sync")
async def sync_inventory():
    result = await inventory_service.sync_inventory(SPREADSHEET_ID)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.get("/inventory/status")
async def get_inventory_status():
    return inventory_service.get_inventory_summary()

@app.post("/forecast/generate")
async def generate_forecasts(forecast_days: int = 30):
    try:
        forecasts = await inventory_service.generate_forecasts(forecast_days)
        return {"forecasts": forecasts, "count": len(forecasts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@app.post("/reorder/create-plans")
async def create_reorder_plans(forecast_days: int = 30):
    try:
        forecasts = await inventory_service.generate_forecasts(forecast_days)
        plans = await inventory_service.create_reorder_plans(forecasts, NOTION_DATABASE_ID)
        
        return {
            "message": f"Created {len(plans)} reorder plans",
            "plans": plans,
            "total_cost": sum(plan.estimated_cost for plan in plans)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reorder plans: {str(e)}")

@app.post("/approval/send")
async def send_approval_requests():
    try:
        pending_plans = []
        for plan_data in inventory_service.reorder_plans.values():
            if plan_data["status"] == "pending":
                pending_plans.append(plan_data["plan"])
        
        if not pending_plans:
            return {"message": "No pending plans to approve"}
        
        result = await inventory_service.send_approval_requests(pending_plans, APPROVER_EMAIL)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send approval requests: {str(e)}")

@app.post("/workflow/auto-replenishment")
async def run_auto_replenishment_workflow():
    try:
        # Step 1: Sync inventory
        sync_result = await inventory_service.sync_inventory(SPREADSHEET_ID)
        if sync_result["status"] == "error":
            raise HTTPException(status_code=500, detail=sync_result["message"])
        
        # Step 2: Generate forecasts
        forecasts = await inventory_service.generate_forecasts(30)
        
        # Step 3: Create reorder plans
        plans = await inventory_service.create_reorder_plans(forecasts, NOTION_DATABASE_ID)
        
        # Step 4: Send approval requests for high priority items
        high_priority_plans = [p for p in plans if p.priority.value == "High"]
        
        approval_result = {"message": "No high priority items"}
        if high_priority_plans:
            approval_result = await inventory_service.send_approval_requests(
                high_priority_plans, APPROVER_EMAIL
            )
        
        return {
            "workflow_status": "completed",
            "items_synced": sync_result.get("items_count", 0),
            "forecasts_generated": len(forecasts),
            "plans_created": len(plans),
            "high_priority_plans": len(high_priority_plans),
            "approval_result": approval_result,
            "total_estimated_cost": sum(plan.estimated_cost for plan in plans)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

@app.get("/reorder/plans")
async def get_reorder_plans():
    plans_data = []
    for item_id, plan_data in inventory_service.reorder_plans.items():
        plans_data.append({
            "item_id": item_id,
            "plan": plan_data["plan"],
            "status": plan_data["status"],
            "notion_page_id": plan_data.get("notion_page_id"),
            "created_at": plan_data.get("created_at")
        })
    
    return {"plans": plans_data, "count": len(plans_data)}

@app.post("/config/update")
async def update_configuration(config: Dict[str, str]):
    global SPREADSHEET_ID, NOTION_DATABASE_ID, APPROVER_EMAIL
    
    if "spreadsheet_id" in config:
        SPREADSHEET_ID = config["spreadsheet_id"]
    
    if "notion_database_id" in config:
        NOTION_DATABASE_ID = config["notion_database_id"]
    
    if "approver_email" in config:
        APPROVER_EMAIL = config["approver_email"]
    
    return {
        "message": "Configuration updated",
        "current_config": {
            "spreadsheet_id": SPREADSHEET_ID,
            "notion_database_id": NOTION_DATABASE_ID,
            "approver_email": APPROVER_EMAIL
        }
    }
