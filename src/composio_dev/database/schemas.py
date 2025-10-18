from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    sku: str
    current_stock: int
    reorder_threshold: int
    supplier_email: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True


class InventoryLogCreate(BaseModel):
    product_id: int
    change: int
    reason: Optional[str] = None


class ReorderPlanCreate(BaseModel):
    product_id: int
    suggested_qty: int
    forecast_period_days: int
    llm_reasoning: Optional[str] = None


class IntegrationCreate(BaseModel):
    user_id: str
    app_name: str
    access_token: str
    refresh_token: Optional[str]
