# 🔧 Services API

## SheetsService
```python
class SheetsService:
    def get_inventory_data(spreadsheet_id, range="A:G") → dict
    def update_stock(spreadsheet_id, row, new_stock) → dict  
    def track_stock_changes(spreadsheet_id) → dict
```

**Usage:**
```python
sheets = SheetsService()
data = sheets.get_inventory_data("sheet_id")
low_stock = sheets.track_stock_changes("sheet_id")
sheets.update_stock("sheet_id", row=2, new_stock=25)
```

## NotionService
```python
class NotionService:
    def create_reorder_plan(database_id, item_data) → dict
    def update_reorder_status(page_id, status) → dict
    def get_pending_orders(database_id) → dict
```

**Usage:**
```python
notion = NotionService()
item = {"item_name": "Pens", "current_stock": 5, "min_threshold": 10}
notion.create_reorder_plan("db_id", item)
notion.update_reorder_status("page_id", "Approved")
```

## InventoryTracker
```python
class InventoryTracker:
    async def sync_and_track() → dict  # Main workflow
    def update_stock_level(row, new_stock) → dict
    def get_inventory_status() → dict
```

**Usage:**
```python
tracker = InventoryTracker("sheet_id", "notion_db_id")
result = await tracker.sync_and_track()
tracker.update_stock_level(2, 30)
```

## Data Structures

### Inventory Item
```python
{
    "item_id": "ITEM001",
    "item_name": "Office Pens",
    "current_stock": 8,
    "min_threshold": 10,
    "supplier": "ABC Corp"
}
```

### Redis Alert
```python
{
    "item_name": "Office Pens",
    "current_stock": 8,
    "min_threshold": 10,
    "supplier": "ABC Corp",
    "priority": "High"
}
```

## Error Handling
All services return `{"error": "message"}` on failure.

## Composio Actions
- **GOOGLESHEETS_READ_RANGE**: Read sheet data
- **GOOGLESHEETS_UPDATE_RANGE**: Update cells
- **NOTION_CREATE_PAGE**: Create reorder plan
- **GMAIL_SEND_EMAIL**: Send notifications

## 🔗 Navigation
- ⬅️ [Docs Home](../README.md)
- 🏗️ [Architecture Overview](../architecture/system-overview.md)
- 📊 [Data Flow](../architecture/data-flow.md)
- 📋 [Data Models](models.md)
- 🧪 [Testing Guide](testing.md)