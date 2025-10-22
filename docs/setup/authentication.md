# Authentication Setup

## Overview

The system uses Composio for managing OAuth2 connections to Google Sheets, Gmail, and Notion. This guide walks through setting up each integration.

## Composio Platform Setup

### 1. Create Composio Account

1. Visit [app.composio.dev](https://app.composio.dev)
2. Sign up with your email
3. Verify your account
4. Access the dashboard

### 2. Get API Credentials

```bash
# From Composio Dashboard
1. Go to Settings → API Keys
2. Create new API key
3. Copy the key → Add to .env as COMPOSIO_API_KEY

# Generate User ID (use your app name + UUID)
COMPOSIO_USER_ID=inventory-copilot-{generate-uuid}
```

## Gmail Integration

### 1. Create Gmail Auth Config

1. **Navigate**: Composio Dashboard → Auth Configs
2. **Create New**: Click "Create Auth Config"
3. **Select App**: Choose "Gmail"
4. **Auth Type**: Select "OAuth2"
5. **Configuration**:
   ```json
   {
     "client_id": "your_google_client_id",
     "client_secret": "your_google_client_secret",
     "scope": [
       "https://www.googleapis.com/auth/gmail.send",
       "https://www.googleapis.com/auth/gmail.readonly"
     ]
   }
   ```
6. **Save**: Copy the Auth Config ID
7. **Add to .env**: `COMPOSIO_GMAIL_ACCOUNT_ID=your_auth_config_id`

### 2. Google Cloud Console Setup

1. **Create Project**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Enable APIs**:
   - Gmail API
   - Google Sheets API
3. **Create Credentials**:
   - OAuth 2.0 Client IDs
   - Application type: Web application
   - Authorized redirect URIs: `https://backend.composio.dev/api/v1/auth/oauth2/callback`
4. **Copy Credentials**: Use in Composio Auth Config

### 3. Test Gmail Connection

```python
# Test script: test_gmail_auth.py
import os
from dotenv import load_dotenv
from composio import ComposioToolSet, App

load_dotenv()

def test_gmail_connection():
    toolset = ComposioToolSet(entity_id=os.getenv("COMPOSIO_USER_ID"))
    
    # Check existing connections
    accounts = toolset.get_connected_accounts()
    print(f"Connected accounts: {len(accounts)}")
    
    # If no Gmail connection, initiate OAuth
    gmail_connected = any(acc.app == App.GMAIL for acc in accounts)
    
    if not gmail_connected:
        print("Initiating Gmail OAuth...")
        connection_request = toolset.initiate_connection(
            app=App.GMAIL,
            integration_id=os.getenv("COMPOSIO_GMAIL_ACCOUNT_ID")
        )
        print(f"Visit: {connection_request.redirect_url}")
        print("Complete OAuth flow in browser")
    else:
        print("✅ Gmail already connected!")

if __name__ == "__main__":
    test_gmail_connection()
```

## 📊 Google Sheets Integration

### 1. Create Sheets Auth Config

1. **Composio Dashboard**: Auth Configs → Create New
2. **Select**: Google Sheets
3. **OAuth2 Configuration**:
   ```json
   {
     "client_id": "same_as_gmail_client_id",
     "client_secret": "same_as_gmail_client_secret", 
     "scope": [
       "https://www.googleapis.com/auth/spreadsheets",
       "https://www.googleapis.com/auth/drive.readonly"
     ]
   }
   ```
4. **Save Config ID**: Add to .env as `COMPOSIO_SHEETS_ACCOUNT_ID`

### 2. Prepare Google Sheets

Create a spreadsheet with this structure:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Item ID | Item Name | Current Stock | Min Threshold | Daily Usage | Supplier | Unit Cost |
| ITEM001 | Office Pens | 25 | 10 | 2 | ABC Corp | 1.50 |
| ITEM002 | Notebooks | 8 | 15 | 1 | XYZ Ltd | 2.00 |

**Get Spreadsheet ID**:
```
URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
Copy the SPREADSHEET_ID part
```

### 3. Test Sheets Connection

```python
# Test script: test_sheets_auth.py
from composio_dev.services.sheets_service import SheetsService

def test_sheets():
    sheets = SheetsService()
    
    if sheets.connected:
        print("✅ Sheets connected!")
        
        # Test reading data
        result = sheets.get_inventory_data("your_spreadsheet_id")
        print(f"Data result: {result}")
    else:
        print("❌ Sheets not connected")

if __name__ == "__main__":
    test_sheets()
```

## Notion Integration

### 1. Create Notion Integration

1. **Notion Developers**: [developers.notion.com](https://developers.notion.com)
2. **Create Integration**: 
   - Name: "Inventory Copilot"
   - Capabilities: Read, Write, Insert content
3. **Get Token**: Copy Internal Integration Token
4. **Composio Setup**:
   - Auth Configs → Create New → Notion
   - Use Integration Token

### 2. Setup Notion Database

Create database with these properties:

| Property | Type | Options |
|----------|------|---------|
| Item | Title | - |
| Current Stock | Number | - |
| Depletion Date | Date | - |
| Order Quantity | Number | - |
| Supplier | Text | - |
| Cost | Number | Currency |
| Priority | Select | High, Medium, Low |
| Status | Select | Pending Approval, Approved, Rejected |

**Get Database ID**:
```
URL: https://notion.so/DATABASE_ID?v=...
Copy the DATABASE_ID part (32 characters)
```

### 3. Share Database with Integration

1. **Open Database**: In Notion
2. **Share**: Click Share button
3. **Invite**: Add your integration by name
4. **Permissions**: Give Edit access

### 4. Test Notion Connection

```python
# Test script: test_notion_auth.py
from composio_dev.services.notion_service import NotionService

def test_notion():
    notion = NotionService()
    
    if notion.connected:
        print("✅ Notion connected!")
        
        # Test creating a page
        test_item = {
            "item_name": "Test Item",
            "current_stock": 5,
            "min_threshold": 10,
            "supplier": "Test Supplier"
        }
        
        result = notion.create_reorder_plan("your_database_id", test_item)
        print(f"Create result: {result}")
    else:
        print("❌ Notion not connected")

if __name__ == "__main__":
    test_notion()
```

## 🔍 Authentication Troubleshooting

### Common Issues

**OAuth Redirect Errors**:
```bash
# Ensure redirect URI in Google Console matches:
https://backend.composio.dev/api/v1/auth/oauth2/callback
```

**Permission Denied**:
```bash
# Check scopes in auth config match required permissions
# Gmail: gmail.send, gmail.readonly
# Sheets: spreadsheets, drive.readonly
```

**Connection Not Found**:
```python
# List all connections
from composio import ComposioToolSet
toolset = ComposioToolSet(entity_id="your_user_id")
accounts = toolset.get_connected_accounts()
for acc in accounts:
    print(f"App: {acc.app}, ID: {acc.id}")
```

### Verification Script

```python
# verify_auth.py - Complete authentication check
import os
from dotenv import load_dotenv
from composio import ComposioToolSet, App

def verify_all_connections():
    load_dotenv()
    
    toolset = ComposioToolSet(entity_id=os.getenv("COMPOSIO_USER_ID"))
    accounts = toolset.get_connected_accounts()
    
    required_apps = [App.GMAIL, App.GOOGLESHEETS, App.NOTION]
    
    print("🔍 Authentication Status")
    print("=" * 40)
    
    for app in required_apps:
        connected = any(acc.app == app for acc in accounts)
        status = "✅ Connected" if connected else "❌ Not Connected"
        print(f"{app.value}: {status}")
    
    print(f"\nTotal connections: {len(accounts)}")
    
    return len([acc for acc in accounts if acc.app in required_apps]) == len(required_apps)

if __name__ == "__main__":
    all_connected = verify_all_connections()
    print(f"\n{'✅ All services connected!' if all_connected else '❌ Some services need setup'}")
```

## Navigation
- [Docs Home](../README.md)
- [Installation](installation.md)
- [Environment Config](environment.md)
- [Architecture Overview](../architecture/system-overview.md)
- [Workflow Guide](../architecture/workflow.md)
- [Testing Guide](../api/testing.md)