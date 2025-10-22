# 🧪 Testing Guide

## Quick Tests

### Individual Services
```bash
# Test Sheets connection and CRUD operations
python composio_dev/services_testing/test_crud_operations.py

# Test AI email generation  
python composio_dev/services_testing/test_email_send.py

# Test Notion integration
python composio_dev/services_testing/test_notion_actions.py
```

### Full Workflow
```bash
# Complete integration test
python composio_dev/services_testing/test_inventory_tracker.py
```

## Redis messaging test

```bash
# Start server
cd inventory_pulse/src
uvicorn app:app --port 8000 --reload

# Test alert simulation
curl -X POST "http://localhost:8000/simulate_low_stock_alert/"
```

## Expected Results

### Working Features ✅
- Gmail OAuth2 connection
- AI email generation & parsing
- Redis pub/sub messaging
- Google Sheets CRUD operations
- Notion page actions

### Test Output
```
✅ Gmail connected successfully!
✅ Email generation successful!
✅ Low stock items detected: 2
✅ Reorder plans created: 2
✅ Redis alerts published: 2
```

## Troubleshooting

**Connection Issues:**
- Verify `.env` variables are set
- Check Composio auth configs
- Ensure OAuth flow completed

**Test Failures:**
- Update spreadsheet/database IDs
- Check Redis server is running
- Verify API keys are valid

## Mock Data
Tests use sample inventory data:
```python
{
    "item_name": "Office Pens",
    "current_stock": 5,
    "min_threshold": 10,
    "supplier": "ABC Corp"
}
```

## 🔗 Navigation
- ⬅️ [Docs Home](../README.md)
- 🚀 [Setup Guide](../setup/installation.md)
- 🔐 [Authentication](../setup/authentication.md)
- 🏗️ [Architecture Overview](../architecture/system-overview.md)
- 🔧 [Services API](services.md)
- 📋 [Data Models](models.md)