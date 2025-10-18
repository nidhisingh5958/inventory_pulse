# Database Architecture Diagram

## System Architecture 

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│                            (main.py)                             │
└────────────────┬───────────────────────┬────────────────────────┘
                 │                       │
                 │                       │
                 ▼                       ▼
    ┌────────────────────┐   ┌─────────────────────┐
    │ InventoryService   │   │  Database Session   │
    │  (Updated)         │◄──┤    Dependency       │
    │                    │   │   get_db()          │
    └─────────┬──────────┘   └─────────────────────┘
              │                         │
              │ Uses CRUD               │
              ▼                         ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │   database/crud.py  │   │  SQLAlchemy ORM     │
    │                     │   │   (SessionLocal)    │
    │ - get_product()     │   └──────────┬──────────┘
    │ - create_product()  │              │
    │ - upsert_product()  │              │
    │ - create_log()      │              ▼
    │ - create_plan()     │   ┌─────────────────────┐
    │ - get_plans()       │   │   Database Engine   │
    └─────────┬───────────┘   │    (SQLite/PG)      │
              │               └──────────┬──────────┘
              │                          │
              ▼                          ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │ database/models.py  │   │   inventory.db      │
    │                     │   │                     │
    │ - Product           │   │ ┌─────────────────┐ │
    │ - InventoryLog      │   │ │   products      │ │
    │ - ReorderPlan       │◄──┼─┤                 │ │
    │ - Integration       │   │ │   inventory_logs│ │
    └─────────────────────┘   │ │                 │ │
                              │ │   reorder_plans │ │
                              │ │                 │ │
                              │ │   integrations  │ │
                              │ └─────────────────┘ │
                              └─────────────────────┘
```

## Data Flow

### 1. Sync Inventory from Google Sheets
```
┌────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  Google    │────►│   Composio   │────►│  Inventory  │────►│ Database │
│  Sheets    │     │   Service    │     │   Service   │     │ (upsert) │
└────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                               │
                                               └──────► Creates InventoryLog
```

### 2. Generate Forecasts
```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Database │────►│  Inventory  │────►│   Forecast   │────►│   Groq   │
│(products)│     │   Service   │     │   Service    │     │   LLM    │
└──────────┘     └─────────────┘     └──────────────┘     └──────────┘
                                               │
                                               └──────► Returns Forecasts
```

### 3. Create Reorder Plans
```
┌───────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│ Forecasts │────►│  Inventory  │────►│  Notion  │     │ Database │
│           │     │   Service   │     │   API    │     │(save plan)
└───────────┘     └─────────────┘     └──────────┘     └──────────┘
                         │
                         └──────► Creates ReorderPlan in DB
```

### 4. Send Approval Emails
```
┌──────────┐     ┌─────────────┐     ┌──────────┐
│ Database │────►│  Inventory  │────►│  Gmail   │
│ (pending │     │   Service   │     │   API    │
│  plans)  │     └─────────────┘     └──────────┘
└──────────┘
```

## Database Tables Relationships

```
┌─────────────────────────┐
│       Product           │
│─────────────────────────│
│ • id (PK)               │◄─────┐
│ • item_id (unique)      │      │
│ • name                  │      │
│ • sku                   │      │
│ • current_stock         │      │ 1:N
│ • min_threshold         │      │
│ • daily_usage           │      │
│ • supplier              │      │
│ • unit_cost             │      │
└─────────────────────────┘      │
                                 │
            ┌────────────────────┴────────────────────┐
            │                                         │
            │                                         │
┌───────────▼───────────┐              ┌──────────────▼──────────┐
│   InventoryLog        │              │    ReorderPlan          │
│───────────────────────│              │─────────────────────────│
│ • id (PK)             │              │ • id (PK)               │
│ • product_id (FK)     │              │ • product_id (FK)       │
│ • change              │              │ • predicted_depletion   │
│ • reason              │              │ • recommended_qty       │
│ • created_at          │              │ • estimated_cost        │
└───────────────────────┘              │ • priority              │
                                       │ • justification         │
                                       │ • status                │
                                       │ • notion_page_id        │
                                       └─────────────────────────┘
```

## API Endpoints → Database Operations

| Endpoint                       | Method | Database Operations                                        |
|--------------------------------|--------|------------------------------------------------------------|
| `/inventory/sync`              | POST   | `crud.upsert_product()` + `create_inventory_log()`         |
| `/inventory/status`            | GET    | `crud.get_all_products()` + `get_pending_reorder_plans()`  |
| `/forecast/generate`           | POST   | `crud.get_all_products()` → Process → Return               |
| `/reorder/create-plans`        | POST   | `crud.get_product_by_item_id()` + `create_reorder_plan()`  |
| `/approval/send`               | POST   | `crud.get_pending_reorder_plans()` → Email                 |
| `/reorder/plans`               | GET    | `crud.get_pending_reorder_plans()` + `get_product_by_id()` |
| `/workflow/auto-replenishment` | POST   | All above operations in sequence                           |


## Session Management

```python
# Database session lifecycle per request:

1. Request arrives
   ↓
2. FastAPI dependency: db = SessionLocal()
   ↓
3. Endpoint function executes with db
   ↓
4. Service methods use db for CRUD
   ↓
5. CRUD operations commit changes
   ↓
6. Response sent
   ↓
7. Finally: db.close()
```

## File Structure

```
src/composio_dev/
├── main.py                     
├── models.py                   
├── requirements.txt           
│
├── database/
│   ├── __init__.py            
│   ├── db_config.py           
│   ├── models.py               
│   ├── schemas.py             
│   └── crud.py                 
│
└── services/
    ├── inventory_service.py    
    ├── forecast_service.py     
    └── composio_service.py     
```

