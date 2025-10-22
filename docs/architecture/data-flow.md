# 📊 Data Flow

## Pipeline Overview

```
Raw Sheets → Parsed Objects → Business Logic → Redis Messages → AI Content → Gmail API
     ↓              ↓              ↓              ↓             ↓           ↓
  String[]      Dict{}         Alert{}        JSON{}       Email{}    Result{}
```

## Transformations

### 1. Sheets → Objects
```python
# Input: ["ITEM001", "Pens", "8", "10", "2", "ABC", "1.50"]
# Output:
{
    "item_id": "ITEM001",
    "item_name": "Pens",
    "current_stock": 8,
    "min_threshold": 10,
    "daily_usage": 2,
    "supplier": "ABC",
    "unit_cost": 1.50
}
```

### 2. Low Stock Detection
```python
if current_stock <= min_threshold:
    days_until_depletion = (current_stock - min_threshold) / daily_usage
    priority = "High" if days <= 3 else "Medium" if days <= 7 else "Low"
```

### 3. Redis Alert
```python
alert = {
    "item_name": "Pens",
    "current_stock": 8,
    "min_threshold": 10,
    "supplier": "ABC",
    "priority": "High",
    "timestamp": "2024-01-10T14:30:00"
}
```

### 4. AI Email Generation
```python
context = f"Low stock: {item_name} ({current_stock}/{min_threshold}), supplier {supplier}"
# AI generates professional email content
```

### 5. Notion Plan
```python
{
    "Item": {"title": [{"text": {"content": "Pens"}}]},
    "Current Stock": {"number": 8},
    "Priority": {"select": {"name": "High"}},
    "Status": {"select": {"name": "Pending Approval"}}
}
```

## Validation & Sanitization

### Input Validation
```python
def validate_row(row):
    if len(row) < 5: return False
    try:
        int(row[2])  # current_stock
        int(row[3])  # min_threshold  
        float(row[4])  # daily_usage
        return True
    except ValueError:
        return False
```

### Data Cleaning
```python
def sanitize_data(raw):
    return {
        "item_name": raw["item_name"].strip().title(),
        "current_stock": max(0, int(raw["current_stock"])),
        "min_threshold": max(1, int(raw["min_threshold"]))
    }
```

---

## Error Handling

### Service Failures
```python
try:
    result = service.execute_action(action, params)
except Exception as e:
    return {"error": f"Failed: {str(e)}"}
```

### Data Quality
- Skip malformed rows
- Use default values for missing data
- Log validation errors
- Continue processing valid items

## 🔗 Navigation
- ⬅️ [Docs Home](../README.md)
- ⬅️ [Architecture Overview](system-overview.md)
- ⬅️ [Workflow Guide](workflow.md)
- 🔧 [Services API](../api/services.md)
- 📋 [Data Models](../api/models.md)
- 🧪 [Testing Guide](../api/testing.md)