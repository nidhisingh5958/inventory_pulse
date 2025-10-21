from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class PriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class UserDetails(BaseModel):
    user_id: str
    name: str
    email: str

class GmailServiceResponse(BaseModel):
    recipient_email: str
    subject: str
    body: str

class InventoryItem(BaseModel):
    item_id: str
    name: str
    current_stock: int
    min_threshold: int
    daily_usage: float
    supplier: str
    unit_cost: float

class ForecastResult(BaseModel):
    item_id: str
    item_name: str
    current_stock: int
    predicted_depletion_date: str
    days_until_depletion: int
    confidence_score: float
    risk_factors: List[str]

class ReorderPlan(BaseModel):
    item_id: str
    item_name: str
    current_stock: int
    predicted_depletion_date: str
    recommended_order_quantity: int
    supplier: str
    estimated_cost: float
    priority: PriorityLevel
    justification: str

class ApprovalRequest(BaseModel):
    reorder_plans: List[ReorderPlan]
    approver_email: str