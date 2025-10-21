# 📊 Data Models

## Core Models

### InventoryItem
```python
class InventoryItem(BaseModel):
    item_id: str
    name: str
    current_stock: int
    min_threshold: int
    daily_usage: float
    supplier: str
    unit_cost: float
```

### ReorderPlan
```python
class ReorderPlan(BaseModel):
    item_id: str
    item_name: str
    current_stock: int
    predicted_depletion_date: str
    recommended_order_quantity: int
    supplier: str
    estimated_cost: float
    priority: PriorityLevel  # High/Medium/Low
    justification: str
```

### GmailServiceResponse
```python
class GmailServiceResponse(BaseModel):
    recipient_email: str
    subject: str
    body: str
```

## Data Transformations

### Sheets → InventoryItem
```python
# Raw: ["ITEM001", "Pens", "25", "10", "2", "ABC Corp", "1.50"]
# Parsed:
{
    "item_id": "ITEM001",
    "name": "Pens", 
    "current_stock": 25,
    "min_threshold": 10,
    "daily_usage": 2.0,
    "supplier": "ABC Corp",
    "unit_cost": 1.50
}
```

### InventoryItem → ReorderPlan
```python
# Calculate metrics
days_until_depletion = (current_stock - min_threshold) / daily_usage
order_quantity = max(min_threshold * 2, 50)
priority = "High" if days <= 3 else "Medium" if days <= 7 else "Low"
```

## Validation Rules
- Stock values: Non-negative integers
- Thresholds: Positive integers  
- Costs: Non-negative floats
- Text fields: Non-empty strings
- Dates: Future dates only

## Usage Example
```python
from models.models import InventoryItem, ReorderPlan

# Create item
item = InventoryItem(
    item_id="ITEM001",
    name="Office Pens",
    current_stock=8,
    min_threshold=10,
    daily_usage=2.0,
    supplier="ABC Corp",
    unit_cost=1.50
)

# Generate plan
plan = create_reorder_plan(item)
```

## 🔗 Navigation
- ⬅️ [Docs Home](../README.md)
- 🏗️ [Architecture Overview](../architecture/system-overview.md)
- 📊 [Data Flow](../architecture/data-flow.md)
- 🔧 [Services API](services.md)
- 🧪 [Testing Guide](testing.md)