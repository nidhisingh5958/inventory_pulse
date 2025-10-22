# Architecture

## System Overview
```
Google Sheets ──┐    ┌── Notion
(Inventory)     │    │   (Plans)
                ▼    ▼
            COMPOSIO PLATFORM
                    │
                    ▼
        ┌─────────────────────┐
        │  INVENTORY COPILOT  │
        │ ┌─────┐ ┌─────────┐ │
        │ │Redis│ │Gemini AI│ │
        │ └─────┘ └─────────┘ │
        │ ┌─────────────────┐ │
        │ │   FastAPI       │ │
        │ └─────────────────┘ │
        └─────────────────────┘
                    │
                    ▼
                  Gmail
```

## Core Components

### Services
- **SheetsService**: Read/write Google Sheets inventory
- **NotionService**: Create/manage reorder plans
- **InventoryTracker**: Main workflow orchestrator

### Infrastructure
- **Redis**: Pub/sub messaging for alerts
- **Composio**: OAuth2 + API integration platform
- **Gemini AI**: Professional email generation
- **FastAPI**: Async REST API server

## Data Flow
1. **Monitor** → Sheets inventory levels
2. **Detect** → Low stock conditions
3. **Alert** → Redis pub/sub messages
4. **Generate** → AI email content
5. **Send** → Gmail notifications
6. **Plan** → Notion reorder entries

## Tech Stack
- **Backend**: FastAPI, Redis, Pydantic
- **AI**: Google Gemini 2.0 Flash
- **Integration**: Composio Tool Router
- **External**: Google Sheets, Notion, Gmail

## Architecture Patterns
- **Event-Driven**: Redis pub/sub messaging
- **Service-Oriented**: Modular service design
- **Repository**: Abstracted data access
- **Configuration-Driven**: Environment-based setup

## Navigation
- [Docs Home](../README.md)
- [Setup Guide](../setup/installation.md)
- [Workflow Details](workflow.md)
- [Data Flow](data-flow.md)
- [Services API](../api/services.md)
- [Testing Guide](../api/testing.md)