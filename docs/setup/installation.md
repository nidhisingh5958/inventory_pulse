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
cd inventory_pulse_dev/src
pip install -r requirements.txt
```

### 2. Install Redis

### Instructions for Docker:

```bash
# Run this command to start Redis Stack in detached mode:
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
# access Redis Stack at 👉 http://localhost:8001
```

### Instructions for Local Installation:

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


### 3. Environment Configuration

``` bash
# Copy the .env.sample file to .env and fill in the required values.
```

### 4. Verify Installation

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