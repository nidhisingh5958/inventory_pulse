# 🤖 Inventory Pulse 

AI-powered inventory management system with automated forecasting, reorder planning, and approval workflows using Google Sheets, Notion, and Gmail integration via Composio.

## Composio Integration Documentation

**All Composio integration challenges have been resolved and comprehensively documented:**

📋 [**Friction Log.md**](./Friction_Log.md)  

Complete documentation of all Composio challenges encountered, debugging steps, and solutions implemented.

---

## Problem Statement - Industrial Agents (SMB-focussed)
> Inventory Replenishment Copilot – Track stock in Sheets, forecast depletion via LLMs, update Notion reorder plans, and email approvals via Gmail.

## Team Name
**NeoMinds**

## Team Members
- **Member 1**: Madhur Prakash Mangal - [madhurprakash2005@gmail.com](mailto:madhurprakash2005@gmail.com)

- **Member 2**: Akshat Arya - [akshatarya2507@gmail.com](mailto:akshatarya2507@gmail.com)

- **Member 3**: Nidhi Singh - [nidhisingh5958@gmail.com](mailto:nidhisingh5958@gmail.com)

- **Member 4**: Ansh Johnson - [anshjohnson69@gmail.com](mailto:anshjohnson69@gmail.com)

---

## Demo Video Link
[YouTube Video Link](https://youtube.com)

---

# Project Artefacts

## Technical Documentation
[Technical Docs](/docs/README.md)  
*All technical details are documented in markdown files, including system architecture, implementation details.*

## Source Code

### **Note on Current Implementation**  
The integration of automation workflows via **Composio (Sheets, Notion, Gmail)** has been **successfully implemented** with comprehensive solutions for all encountered challenges. During development, several integration complexities were identified and resolved through extensive debugging and solution implementation.

All challenges, solutions, and implementation details have been **comprehensively documented** for future reference and developer onboarding:

📄 **Complete Composio Implementation Guide:** [`COMPOSIO_COMPREHENSIVE_GUIDE.md`](./COMPOSIO_COMPREHENSIVE_GUIDE.md)  
*Comprehensive documentation covering all Composio integration challenges, complete solutions, best practices, working code examples, and production-ready implementations.*

### **Production-Ready Implementation Available**  
The Composio-powered version is **fully functional and production-ready** with comprehensive error handling, fallback mechanisms, and robust implementations.  
📂 **To explore the complete working implementation:**  
[Working Code Directory](https://github.com/nidhisingh5958/inventory_pulse/tree/main/src/working_code)

---


[GitHub Repository](https://github.com/nidhisingh5958/inventory_pulse/tree/main/src)  
*Complete backend source code with all modules, dependencies, and configurations for successful installation and execution.*

---

## 🚀 Features

- **📊 Google Sheets Integration**: Real-time inventory tracking
- **🤖 AI Forecasting**: Groq LLM-powered depletion prediction
- **📝 Notion Planning**: Automated reorder plan creation
- **📧 Gmail Notifications**: Approval request automation
- **🔄 Complete Workflow**: End-to-end automation

---

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
- **Scalable Design**: Modular services for easy extension and maintenance

---

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

---

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

### **Phase 5: Reorder Planning** (Under Development)
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
- **Google Sheets API (from Composio)**: Inventory data management
- **Notion API (from Composio)**: Reorder plan tracking
- **Gmail API (from Composio)**: Email delivery
- **OAuth2 (from Composio)**: Secure service authentication

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

## 📦 Quick Start

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/nidhisingh5958/inventory_pulse.git
    cd inventory_pulse/src
    ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Redis:
   ```bash
   # Run this command to start Redis Stack in detached mode:
   docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
   # access Redis Stack at 👉 http://localhost:8001
   ```

5. Set up environment variables:

      ``` bash
      # Copy the .env.sample file to .env and fill in the required values.
      ```

---

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn app:app --port 8000 --reload
   ```

2. Access the API documentation at:
   ```bash
   http://127.0.0.1:8000/docs
   # for detailed docs visit 👉 http://127.0.0.1:8000/scalar
   ```


## 🧪 Testing

### **Quick Tests**
```bash
# Individual services
python composio_dev/services_testing/test_sheets_actions.py
python composio_dev/services_testing/test_gemini.py

# Full workflow
python composio_dev/services_testing/test_inventory_tracker.py
```

---

### **Status**
- ✅ **Working**: Gmail, AI email generation, Redis messaging, Sheets reading
- 🚧 **In Progress**: Complete CRUD operations for Notion integration
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