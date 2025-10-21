# 📦 Installation Guide

## Prerequisites

- Python 3.8+
- Redis server
- Google account (for Sheets and Gmail)
- Notion account
- Composio account

## 🔧 Installation Steps

### 1. Clone and Setup Project

```bash
cd inventory_pulse_dev
pip install -r requirements.txt
```

### 2. Install Redis

**Windows:**
```bash
# Using Chocolatey
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

### 3. Start Redis Server

```bash
redis-server
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 4. Environment Configuration

Create `.env` file in project root:

```env
# Composio Configuration
COMPOSIO_API_KEY=your_composio_api_key
COMPOSIO_USER_ID=your_unique_user_id
COMPOSIO_GMAIL_ACCOUNT_ID=your_gmail_auth_config_id

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# Application Configuration
SPREADSHEET_ID=your_google_sheets_id
NOTION_DATABASE_ID=your_notion_database_id
```

### 5. Verify Installation

Run the test suite:
```bash
python composio_dev/services_testing/test_inventory_tracker.py
```

Choose option 1 to test individual services.

## 📋 Dependencies

### Core Dependencies
```
fastapi>=0.104.1
uvicorn>=0.24.0
composio-core>=0.3.0
composio-gemini>=0.1.0
aioredis>=2.0.1
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### AI & Integration
```
google-genai>=0.3.0
groq>=0.4.0
requests>=2.31.0
```

### Development
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

## 🔍 Troubleshooting

### Common Issues

**Redis Connection Error:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
redis-server
```

**Import Errors:**
```bash
# Ensure you're in the project directory
cd inventory_pulse_dev

# Check Python path
python -c "import sys; print(sys.path)"
```

**Composio Authentication:**
```bash
# Verify Composio setup
python -c "from composio import ComposioToolSet; print('Composio OK')"
```

### Environment Variables

Verify all required environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'COMPOSIO_API_KEY',
    'COMPOSIO_USER_ID', 
    'GEMINI_API_KEY',
    'COMPOSIO_GMAIL_ACCOUNT_ID'
]

for var in required_vars:
    value = os.getenv(var)
    print(f"{var}: {'✅ Set' if value else '❌ Missing'}")
```

## 🔗 Navigation
- ⬅️ [Docs Home](../README.md)
- ➡️ [Environment Config](environment.md)
- ➡️ [Authentication Setup](authentication.md)
- 🏗️ [Architecture Overview](../architecture/system-overview.md)
- 🧪 [Testing Guide](../api/testing.md)