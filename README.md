# 🤖 Inventory Pulse

AI-powered inventory management system with automated forecasting, reorder planning, and approval workflows using Google Sheets, Notion, and Gmail integration via Composio.

## 🚀 Features

- **📊 Google Sheets Integration**: Real-time inventory tracking
- **🤖 AI Forecasting**: Groq LLM-powered depletion prediction
- **📝 Notion Planning**: Automated reorder plan creation
- **📧 Gmail Notifications**: Approval request automation
- **🔄 Complete Workflow**: End-to-end automation

# Project Artefacts

## Technical Documentation
[Technical Docs](/docs/README.md)  
*All technical details are documented in markdown files, including system architecture, implementation details.*

## Source Code
[GitHub Repository](https://github.com/nidhisingh5958/inventory_pulse/tree/main/src)  
*Complete backend source code with all modules, dependencies, and configurations for successful installation and execution.*

## 📦 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Add to `.env`:
   ```env
   GROQ_API_KEY=your_groq_key
   COMPOSIO_API_KEY=your_composio_key
   ```

3. **Start Server**
   ```bash
   python run.py
   ```

4. **Access API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 🌐 Key Endpoints

- `POST /workflow/auto-replenishment` - Complete automation
- `POST /inventory/sync` - Sync from Google Sheets
- `POST /forecast/generate` - AI forecasting
- `POST /reorder/create-plans` - Create Notion plans
- `POST /approval/send` - Send Gmail approvals

## 🔧 Configuration

Update system configuration:
```bash
curl -X POST "http://localhost:8000/config/update" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "your_sheets_id",
    "notion_database_id": "your_notion_db_id",
    "approver_email": "manager@company.com"
  }'
```

## 🔄 Workflow

1. **Sync**: Pull inventory from Google Sheets
2. **Forecast**: AI predicts depletion dates
3. **Plan**: Create reorder plans in Notion
4. **Approve**: Send email notifications
5. **Track**: Monitor status and alerts

## 📚 Setup Requirements

### Google Sheets
Create spreadsheet with columns:
- A: Item ID
- B: Item Name
- C: Current Stock
- D: Min Threshold
- E: Daily Usage
- F: Supplier
- G: Unit Cost

### Notion Database
Create database with properties:
- Item (Title)
- Current Stock (Number)
- Depletion Date (Date)
- Order Quantity (Number)
- Supplier (Text)
- Cost (Number)
- Priority (Select)
- Status (Select)

### Composio Setup
1. Sign up at https://app.composio.dev
2. Connect Google Sheets, Notion, and Gmail
3. Get API key and add to `.env`

Built with FastAPI, Composio, and Groq
