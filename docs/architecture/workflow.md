# Workflow

## Complete Process Flow

```
Sheets → Parse → Low Stock → Redis → AI Email → Gmail
   ↓                ↓           ↓
Inventory      Reorder Plans  Notion
```

## Step-by-Step

### 1. Inventory Monitoring
- Read Google Sheets via `GOOGLESHEETS_READ_RANGE`
- Parse rows: `["ITEM001", "Pens", "8", "10", ...]`
- Compare: `current_stock <= min_threshold`

### 2. Alert Generation  
- Publish to Redis channel: `low_stock_alerts`
- Message: `{"item_name": "Pens", "current_stock": 8, "supplier": "ABC"}`

### 3. AI Email Generation
- Context: `"Low stock: Pens (8/10 units), supplier ABC Corp"`
- Gemini AI generates professional email
- Parse JSON response: `{"recipient": "...", "subject": "...", "body": "..."}`

### 4. Email Delivery
- Send via `GMAIL_SEND_EMAIL` action
- Log delivery status

### 5. Reorder Planning
- Calculate metrics: depletion date, order quantity, priority
- Create Notion page via `NOTION_CREATE_PAGE`
- Properties: Item, Stock, Date, Quantity, Priority, Status

## Current Implementation

### Redis Listener
```python
async def redis_listener():
    while True:
        msg = await pubsub.get_message()
        if msg:
            # Generate AI email
            # Send via Gmail
```

## API Endpoints

### Trigger Alert
```bash
POST /simulate_low_stock_alert/
# Publishes mock alert to Redis
```

### Manual Sync
```python
tracker = InventoryTracker(sheet_id, notion_db_id)
result = await tracker.sync_and_track()
```

## Data Flow Example

**Input (Sheets):**
| Item | Stock | Threshold |
|------|-------|-----------|
| Pens | 8     | 10        |

**Alert (Redis):**
```json
{"item_name": "Pens", "current_stock": 8, "priority": "High"}
```

**Email (AI Generated):**
```
Subject: Urgent: Stock Replenishment - Pens
Body: Dear Supplier, we need to reorder Pens (8/10 units)...
```

**Plan (Notion):**
| Item | Stock | Order Qty | Priority | Status |
|------|-------|-----------|----------|--------|
| Pens | 8     | 20        | High     | Pending|

## Navigation
- [Docs Home](../README.md)
- [Architecture Overview](system-overview.md)
- [Data Flow Details](data-flow.md)
- [Services API](../api/services.md)
- [Testing Guide](../api/testing.md)