# 🚀 Composio Quick Reference Guide

A companion to `COMPOSIO_CHALLENGES_AND_SOLUTIONS.md` - Quick lookup for common issues and solutions.

---

## Quick Troubleshooting Flowchart

```
❌ Something Failed?
│
├─→ Is it an EMAIL issue?
│   ├─→ Email not sending? → Check Challenge 3.1: Gmail Integration
│   ├─→ Wrong format? → Use body_type: "html" parameter
│   └─→ Can't find account? → Verify Challenge 2.2: Connected Account Discovery
│
├─→ Is it a NOTION issue?
│   ├─→ Properties not updating? → Challenge 4.1: Property Format Complexity
│   ├─→ Can't create page? → Challenge 4.2: Page Creation vs Update
│   └─→ Getting 404? → Check NOTION_DB_ID environment variable
│
├─→ Is it an AUTH issue?
│   ├─→ OAuth redirect failed? → Challenge 1.1: OAuth Flow Documentation
│   ├─→ Connected account missing? → Challenge 2.2: Account Discovery
│   └─→ Invalid token? → Re-authenticate through Composio dashboard
│
├─→ Is it a PARAMETER issue?
│   ├─→ Unclear what parameters? → Challenge 5.1: Action Schema Discovery
│   ├─→ Getting parameter error? → Check ACTION_SCHEMAS reference
│   └─→ Missing required param? → Add logging to see full error
│
└─→ Is it a RATE LIMIT?
    └─→ Random failures? → Challenge 7.1: Add exponential backoff
```

---

## Common Commands & Code Snippets

### Check Connection Status
```python
from composio import ComposioToolSet, App
toolset = ComposioToolSet(entity_id="your_user_id")

# List all connected accounts
accounts = toolset.get_connected_accounts()
for acc in accounts:
    print(f"{acc.appName}: {acc.id} ({acc.status})")
```

### Find Active Account
```python
# Gmail
gmail_accounts = [acc.id for acc in accounts if acc.appName.lower() == 'gmail' and acc.status == 'ACTIVE']
gmail_id = gmail_accounts[0] if gmail_accounts else None

# Notion
notion_accounts = [acc.id for acc in accounts if acc.appName.lower() == 'notion' and acc.status == 'ACTIVE']
notion_id = notion_accounts[0] if notion_accounts else None
```

### Send Email via Composio
```python
from composio import Action

# Required parameters
params = {
    "to": "recipient@example.com",
    "subject": "Your Subject",
    "body": "<p>HTML content</p>",
    "body_type": "html"  # IMPORTANT: Specify HTML type
}

result = toolset.execute_action(
    action=Action.GMAIL_SEND_EMAIL,
    params=params,
    connected_account_id=gmail_account_id
)
```

### Update Notion Page
```python
# Property formatting is critical!
properties = {
    "Title": {
        "title": [{"text": {"content": "Page Title"}}]
    },
    "Status": {
        "select": {"name": "Pending"}
    },
    "Count": {
        "number": 42
    },
    "Description": {
        "rich_text": [{"text": {"content": "Detailed description here"}}]
    },
    "Last Updated": {
        "date": {"start": "2025-10-22T00:00:00"}
    }
}

result = toolset.execute_action(
    action=Action.NOTION_UPDATE_PAGE,
    params={
        "page_id": "your_page_id",
        "properties": properties
    },
    connected_account_id=notion_account_id
)
```

### With Error Handling & Retry
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def execute_action_safe(action, params, account_id):
    try:
        return toolset.execute_action(
            action=action,
            params=params,
            connected_account_id=account_id
        )
    except ValueError as e:
        print(f"Parameter error: {e}")
        raise
    except ConnectionError as e:
        print(f"Connection error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

---

## Environment Variable Checklist

```bash
# Copy to .env and fill in your values

# Composio Core
COMPOSIO_API_KEY=sk_your_key_here
COMPOSIO_USER_ID=your_unique_id

# Gmail (from Composio dashboard > Auth Configs)
COMPOSIO_GMAIL_ACCOUNT_ID=ac_your_gmail_config_id

# Notion (from Composio dashboard > Auth Configs)
COMPOSIO_NOTION_ACCOUNT_ID=ac_your_notion_config_id

# Sheets (from Composio dashboard > Auth Configs)
COMPOSIO_SHEETS_ACCOUNT_ID=ac_your_sheets_config_id

# Google Cloud
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret

# Notion
NOTION_DATABASE_ID=your_db_id_without_dashes

# Sheets
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id

# AI
GEMINI_API_KEY=your_gemini_key

# Debugging
DEBUG=false
LOG_LEVEL=INFO
DEMO_MODE=true  # Set to false for production!
```

---

## Property Type Reference for Notion

When updating Notion pages, use these formats:

```python
# TEXT / TITLE
"Title": {"title": [{"text": {"content": "My Title"}}]}

# RICH TEXT
"Description": {"rich_text": [{"text": {"content": "Rich text content"}}]}

# NUMBER
"Quantity": {"number": 42}

# SELECT (Dropdown)
"Status": {"select": {"name": "Pending Approval"}}  # Name must match existing option

# MULTI_SELECT
"Tags": {"multi_select": [{"name": "Important"}, {"name": "Urgent"}]}

# DATE
"Due Date": {"date": {"start": "2025-10-22"}}

# CHECKBOX
"Completed": {"checkbox": True}

# EMAIL
"Contact": {"email": "user@example.com"}

# URL
"Website": {"url": "https://example.com"}

# PEOPLE (requires user IDs)
"Assigned To": {"people": [{"id": "user_id"}]}

# ROLLUP (read-only via API)
# FORMULA (read-only via API)
# RELATION (for linking databases)
```

---

## Common Error Messages & Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `No active Gmail connected account found` | Gmail not authenticated | Re-authenticate via Composio dashboard |
| `Database not found` | Wrong NOTION_DB_ID | Verify ID format and value in .env |
| `Invalid parameter: body` | Email body format wrong | Set `body_type: "html"` for HTML emails |
| `Property not found: Status` | Notion property doesn't exist | Create property in Notion database first |
| `Authentication failed` | Invalid API key | Check COMPOSIO_API_KEY in .env |
| `429 Too Many Requests` | Rate limit hit | Add exponential backoff retry logic |
| `Connection timeout` | Network/service issue | Retry after delay, check service status |
| `OAuth redirect mismatch` | Wrong redirect URI | Use `https://backend.composio.dev/api/v1/auth/oauth2/callback` |

---

## Demo Mode Development

Always start with demo mode enabled:

```python
# development/.env.local
DEMO_MODE=true  # Don't send real emails
LOG_LEVEL=DEBUG
```

```python
# In your connector classes
connector = ComposioEmailConnector(demo_mode=True)
result = connector.send_email(to, subject, body)
# File saved to demo/outbox/ instead of sent
```

### View Demo Outputs
```bash
# Check what was "sent" in demo mode
ls -la demo/outbox/
cat demo/outbox/composio_*.html
```

---

## Testing Checklist

- [ ] Connected account exists and is ACTIVE
- [ ] Required environment variables are set
- [ ] Demo mode works (test without Composio)
- [ ] Real mode works with mock (if using mocks)
- [ ] Error messages are clear and helpful
- [ ] Retry logic handles transient failures
- [ ] Logging shows full context (action, params, account)
- [ ] No real data sent during development
- [ ] Tests can run without live connections
- [ ] Configuration can be verified on startup

---

## Debugging Tips

### 1. Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Now all composio calls will log detailed info
```

### 2. Print Action Before Execution
```python
print(f"Executing {action_name}")
print(f"Parameters: {params}")
print(f"Account ID: {account_id}")
# Then execute and see what fails
```

### 3. Check Composio Dashboard
- Go to https://app.composio.dev/auth-configs
- Verify your auth configs exist
- Check if connected accounts are ACTIVE
- Look at connection details and permissions

### 4. Verify Notion Database
- Open database in browser
- Check all required properties exist
- Verify property types match your code
- Test manual property updates work

### 5. Use Demo Mode
- Switch to demo mode for development
- All operations write to files instead
- Inspect files to see what was created
- Fast iteration without API calls

---

## Performance Optimization

### For Batch Operations
```python
# Process in queue with delays
import time
from collections import deque

queue = deque(items_to_process)
max_concurrent = 3

while queue:
    # Process up to max_concurrent items
    batch = [queue.popleft() for _ in range(min(max_concurrent, len(queue)))]
    
    for item in batch:
        try:
            execute_action_with_backoff(item)
        except Exception as e:
            logger.error(f"Failed to process {item}: {e}")
    
    # Wait before next batch
    time.sleep(1)  # Rate limit protection
```

### Monitor Rate Limits
```python
import time

attempt = 0
max_attempts = 3

for attempt in range(max_attempts):
    try:
        result = toolset.execute_action(...)
        break  # Success
    except Exception as e:
        if attempt < max_attempts - 1:
            wait_time = (2 ** attempt)  # Exponential: 1s, 2s, 4s
            print(f"Attempt {attempt+1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            raise
```

---

## Quick Reference: File Locations

```
📦 inventory_pulse/
├── 📄 COMPOSIO_CHALLENGES_AND_SOLUTIONS.md  ← Comprehensive guide (YOU ARE HERE)
├── 📄 COMPOSIO_QUICK_REFERENCE.md          ← This file
├── 📄 README.md                             ← Main project readme
├── .env.example                             ← Environment template
├── docs/
│   ├── setup/authentication.md              ← Auth setup details
│   ├── setup/environment.md                 ← Env config details
│   └── setup/installation.md                ← Installation steps
└── src/
    ├── composio_dev/
    │   ├── helper/utils.py                  ← Connection utilities
    │   └── services/                        ← Service implementations
    └── working_code/
        └── src/connectors/
            ├── composio_email_connector_class.py
            ├── composio_email_connector.py
            └── composio_notion_connector.py
```

---

## Getting Help

### If you're stuck:

1. **Check the full guide**: `COMPOSIO_CHALLENGES_AND_SOLUTIONS.md`
2. **Review your error**: Match to "Common Error Messages & Solutions" above
3. **Enable debug logging**: Add detailed print statements
4. **Check Composio Dashboard**: Verify auth configs and connections
5. **Test in demo mode**: Isolate Composio issues
6. **Review the code**: Check implementations in `src/working_code/src/connectors/`

### Resources:
- [Composio Official Docs](https://docs.composio.dev)
- [Composio GitHub Examples](https://github.com/composio/composio)
- Main Guide: `COMPOSIO_CHALLENGES_AND_SOLUTIONS.md`

---

**Last Updated**: October 22, 2025  
**Document Type**: Quick Reference  
**Part of**: Inventory Pulse Project Documentation

