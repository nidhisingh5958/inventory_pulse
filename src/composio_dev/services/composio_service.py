import os
from typing import List, Optional
from models import InventoryItem, ReorderPlan

class ComposioService:
    def __init__(self):
        self.api_key = os.getenv("COMPOSIO_API_KEY")
        self.mock_mode = True  # Enable mock mode for testing
    
    async def sync_inventory_from_sheets(self, spreadsheet_id: str, range_name: str = "A:G") -> List[InventoryItem]:
        if self.mock_mode:
            # Return mock inventory data for testing
            return [
                InventoryItem(
                    item_id="ITM001",
                    name="Office Paper",
                    current_stock=50,
                    min_threshold=100,
                    daily_usage=25.0,
                    supplier="Office Supplies Co",
                    unit_cost=0.05
                ),
                InventoryItem(
                    item_id="ITM002",
                    name="Printer Ink",
                    current_stock=15,
                    min_threshold=10,
                    daily_usage=3.0,
                    supplier="Tech Solutions",
                    unit_cost=15.99
                ),
                InventoryItem(
                    item_id="ITM003",
                    name="Pens",
                    current_stock=200,
                    min_threshold=50,
                    daily_usage=12.0,
                    supplier="Stationery Plus",
                    unit_cost=0.75
                )
            ]
        
        # Real Composio implementation would go here
        raise Exception("Composio integration not configured. Using mock data.")
    
    async def create_notion_reorder_plan(self, database_id: str, plan: ReorderPlan) -> Optional[str]:
        if self.mock_mode:
            # Mock Notion page creation
            print(f"📝 [MOCK] Created Notion page for {plan.item_name}")
            print(f"   Priority: {plan.priority.value}")
            print(f"   Cost: ${plan.estimated_cost:.2f}")
            return f"mock_page_id_{plan.item_id}"
        
        # Real Composio implementation would go here
        raise Exception("Composio integration not configured")
    
    async def send_approval_email(self, to_email: str, subject: str, body: str, plans: List[ReorderPlan]) -> bool:
        if self.mock_mode:
            # Mock email sending
            total_cost = sum(plan.estimated_cost for plan in plans)
            print(f"📧 [MOCK] Sending email to {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Plans: {len(plans)} items")
            print(f"   Total Cost: ${total_cost:.2f}")
            for plan in plans:
                print(f"   - {plan.item_name}: ${plan.estimated_cost:.2f} ({plan.priority.value})")
            return True
        
        # Real Composio implementation would go here
        raise Exception("Composio integration not configured")
    
    def get_available_actions(self) -> List[str]:
        if self.mock_mode:
            return ["mock_googlesheets", "mock_notion", "mock_gmail"]
        
        return []