# 🤖 Inventory Replenishment Copilot

> **AI-powered inventory automation** that eliminates manual stock monitoring and supplier communication.

## 🎯 What This Agent Does

**Problem Solved**: Manual inventory management is time-consuming, error-prone, and leads to stockouts or overstock situations.

**Solution**: Automated AI agent that:
- 📊 **Monitors** inventory levels in Google Sheets
- 🚨 **Detects** low stock situations automatically  
- 🤖 **Generates** professional supplier emails using Gemini AI
- 📧 **Sends** reorder requests via Gmail
- 📝 **Creates** structured reorder plans in Notion
- ⚡ **Processes** everything in real-time via Redis

## 💡 Why It's Innovative

- **AI-First Approach**: Uses Gemini AI for contextual, professional communication
- **Zero-Code Integration**: Composio handles all API complexities
- **Event-Driven Architecture**: Real-time processing with Redis pub/sub
- **Multi-Platform Orchestration**: Seamlessly connects Sheets, Notion, and Gmail
- **Intelligent Prioritization**: Calculates urgency based on depletion rates

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Google Sheets  │    │     Notion      │    │     Gmail       │
│   📊 Inventory  │    │  📋 Reorder     │    │  📧 Supplier    │
│   Tracking      │    │   Planning      │    │  Communication  │
└─────────┬───────┘    └─────────▲───────┘    └─────────▲───────┘
          │                      │                      │
          │ Read Data            │ Create Plans         │ Send Emails
          ▼                      │                      │
┌─────────────────────────────────────────────────────────────────┐
│                 🤖 INVENTORY COPILOT CORE                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Sheets    │  │   Notion    │  │ Inventory   │  │ Gemini  │ │
│  │  Service    │  │  Service    │  │  Tracker    │  │   AI    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Redis Messaging                         │   │
│  │        Real-time Alert Processing                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 FastAPI Server                          │   │
│  │           REST Endpoints & Workflow                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    COMPOSIO     │
                    │   Integration   │
                    │    Platform     │
                    └─────────────────┘
```

## 🔄 Complete Workflow

### **Phase 1: Inventory Monitoring**
```
Google Sheets → Sheets Service → Parse Data → Identify Low Stock
```
1. **Data Source**: Inventory stored in Google Sheets with columns:
   - Item ID, Name, Current Stock, Min Threshold, Daily Usage, Supplier, Cost
2. **Monitoring**: Sheets Service reads inventory data via Composio
3. **Analysis**: Compare current stock vs minimum thresholds
4. **Detection**: Flag items requiring reorder

### **Phase 2: Alert Generation**
```
Low Stock Items → Redis Channel → Background Listener → Process Alert
```
1. **Publishing**: Low stock items published to Redis `low_stock_alerts` channel
2. **Listening**: FastAPI background task continuously monitors Redis
3. **Processing**: Extract alert data and prepare for email generation
4. **Queuing**: Maintain alert queue for batch processing

### **Phase 3: AI Email Generation**
```
Alert Context → Gemini AI → Professional Email → JSON Response
```
1. **Context Building**: Create detailed context from alert data:
   ```
   "I am running low on stocks, draft an email to my supplier ABC Corp.
   Current stock left: 8 units, Daily demand: 2 units.
   Request to replenish as soon as possible."
   ```
2. **AI Processing**: Gemini AI generates professional email content
3. **Response Parsing**: Convert AI response to structured JSON format
4. **Validation**: Ensure all required fields (recipient, subject, body) are present

### **Phase 4: Email Delivery**
```
Email JSON → Gmail API → Supplier Notification → Delivery Confirmation
```
1. **Gmail Integration**: Use Composio Gmail action to send emails
2. **Professional Format**: AI-generated content maintains business tone
3. **Delivery Tracking**: Log success/failure status
4. **Error Handling**: Retry failed deliveries with exponential backoff

### **Phase 5: Reorder Planning** (Integrated)
```
Low Stock Items → Notion Service → Structured Plans → Approval Workflow
```
1. **Plan Creation**: Generate reorder plans with calculated metrics:
   - Depletion date prediction
   - Recommended order quantity (2x safety stock)
   - Priority level (High/Medium/Low based on urgency)
   - Cost estimation
2. **Notion Integration**: Create structured database entries
3. **Status Tracking**: Monitor approval workflow
4. **Plan Updates**: Handle approvals and rejections

## 🛠️ Technical Implementation

### **Core Technologies**
- **FastAPI**: Async web framework for REST API
- **Redis**: Real-time messaging and event processing
- **Composio**: Unified integration platform for external services
- **Gemini AI**: Advanced language model for email generation
- **Pydantic**: Data validation and serialization

### **Integration Stack**
- **Google Sheets API**: Inventory data management
- **Notion API**: Reorder plan tracking
- **Gmail API**: Email delivery
- **OAuth2**: Secure service authentication

### **Key Services**

#### **SheetsService** (`sheets_service.py`)
```python
class SheetsService:
    def get_inventory_data(spreadsheet_id) → dict
    def update_stock(spreadsheet_id, row, new_stock) → dict
    def track_stock_changes(spreadsheet_id) → dict
```

#### **NotionService** (`notion_service.py`)
```python
class NotionService:
    def create_reorder_plan(database_id, item_data) → dict
    def update_reorder_status(page_id, status) → dict
    def get_pending_orders(database_id) → dict
```

#### **InventoryTracker** (`inventory_tracker.py`)
```python
class InventoryTracker:
    async def sync_and_track() → dict  # Main orchestration
    def update_stock_level(row, new_stock) → dict
    def get_inventory_status() → dict
```

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
git clone <repository>
cd inventory_pulse_dev
pip install -r requirements.txt
```

### **2. Required Credentials & Setup**

#### **Get API Keys:**
- **Composio**: [app.composio.dev](https://app.composio.dev) → API Keys
- **Gemini AI**: [aistudio.google.com](https://aistudio.google.com) → Create API Key
- **Google Sheets/Gmail**: Via Composio OAuth (see below)
- **Notion**: [developers.notion.com](https://developers.notion.com) → New Integration

#### **Environment Variables (.env):**
```env
# Required
COMPOSIO_API_KEY=ak_your_composio_key
COMPOSIO_USER_ID=your_unique_user_id  
COMPOSIO_GMAIL_ACCOUNT_ID=ac_your_gmail_config
GEMINI_API_KEY=AIza_your_gemini_key

# Optional
SPREADSHEET_ID=your_google_sheets_id
NOTION_DATABASE_ID=your_notion_database_id
```

### **3. Composio Tool Router Setup**

#### **Connect Third-Party Tools:**
```bash
# 1. Create Gmail Auth Config in Composio Dashboard
# Go to: https://app.composio.dev/auth-configs
# Create OAuth2 config for Gmail with scopes:
# - https://www.googleapis.com/auth/gmail.send
# - https://www.googleapis.com/auth/spreadsheets

# 2. Test connections
python composio_dev/services_testing/test_inventory_tracker.py
```

#### **For Demo/Testing:**
Testers need to provide:
- Composio API key
- Gmail auth config ID (from Composio dashboard)
- Gemini API key
- Test Google Sheets ID
- Test Notion database ID

### **4. Run Locally**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start API
python app.py

# Terminal 3: Test
curl -X POST "http://localhost:8000/simulate_low_stock_alert/"
```

### **5. Verify Setup**
```bash
# Test individual services
python composio_dev/services_testing/test_sheets_actions.py
python composio_dev/services_testing/test_gemini.py
```

## 🧪 Testing

### **Quick Tests**
```bash
# Individual services
python composio_dev/services_testing/test_sheets_actions.py
python composio_dev/services_testing/test_gemini.py

# Full workflow
python composio_dev/services_testing/test_inventory_tracker.py

# API endpoint
curl -X POST "http://localhost:8000/simulate_low_stock_alert/"
```

### **Status**
- ✅ **Working**: Gmail, AI email generation, Redis messaging, Sheets reading
- 🚧 **In Progress**: Complete CRUD operations, error handling
- 📋 **Planned**: Webhooks, ML forecasting, approval workflows

## 📊 Data Flow Example

### **Sample Inventory Data** (Google Sheets)
| Item ID | Item Name | Current Stock | Min Threshold | Daily Usage | Supplier | Unit Cost |
|---------|-----------|---------------|---------------|-------------|----------|-----------|
| ITEM001 | Office Pens | 8 | 10 | 2 | ABC Corp | 1.50 |
| ITEM002 | Notebooks | 25 | 15 | 1 | XYZ Ltd | 2.00 |

### **Generated Alert** (Redis Message)
```json
{
    "item_name": "Office Pens",
    "current_stock": 8,
    "min_threshold": 10,
    "supplier": "ABC Corp",
    "email": "supplier@abc.com",
    "priority": "High",
    "depletion_date": "2024-01-15"
}
```

### **AI-Generated Email**
```json
{
    "recipient_email": "supplier@abc.com",
    "subject": "Urgent: Stock Replenishment Required - Office Pens",
    "body": "Dear ABC Corp,\n\nWe are currently experiencing low stock levels for Office Pens. Current inventory: 8 units, which is below our minimum threshold of 10 units.\n\nWith daily usage of 2 units, we anticipate stockout by January 15, 2024. Please expedite replenishment to avoid service disruption.\n\nBest regards,\nInventory Management Team"
}
```

### **Notion Reorder Plan**
| Property | Value |
|----------|-------|
| Item | Office Pens |
| Current Stock | 8 |
| Depletion Date | 2024-01-15 |
| Order Quantity | 20 |
| Supplier | ABC Corp |
| Cost | $30.00 |
| Priority | High |
| Status | Pending Approval |

## 📚 Documentation

**Quick Links:**
- 🚀 [Setup Guide](docs/setup/installation.md) - Installation & environment
- 🔐 [Authentication](docs/setup/authentication.md) - Composio OAuth setup
- 🏗️ [Architecture](docs/architecture/system-overview.md) - System design
- 🔄 [Workflow](docs/architecture/workflow.md) - Process flow
- 📊 [Data Flow](docs/architecture/data-flow.md) - Data pipeline
- 🔧 [Services API](docs/api/services.md) - Service documentation
- 📋 [Data Models](docs/api/models.md) - Schema definitions
- 🧪 [Testing](docs/api/testing.md) - Test guides
- 📚 [Docs Overview](docs/README.md) - Documentation index

## 🤝 Contributing

1. Fork & create feature branch
2. Follow existing patterns
3. Add tests for new features
4. Update documentation
5. Submit pull request

**Development Status**: Active prototype showcasing AI-powered automation with Composio integration.

---

**Tech Stack**: FastAPI • Composio • Gemini AI • Redis • Google Sheets • Notion • Gmail