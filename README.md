# Inventory Pulse

<h2>Project Structure </h2>

inventory_pulse/
├── src/
│   ├── db/
│   │   ├── base.py           # SQLAlchemy setup
│   │   ├── models.py         # ORM models
│   │   ├── crud.py           # Database operations
│   │   └── session.py        # Session management
│   └── utils/
│       └── schemas.py        # Pydantic models for API I/O