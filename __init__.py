""" File Structure and overview of app

├── .env
├── main_backend.py      # FastAPI Central Core Runner Entry
├── main_frontend.py     # Streamlit Core Orchestrator Layout Entry
├── backend/
│   ├── __init__.py
│   ├── config.py        # Environment variables & API client init
│   ├── db_core.py       # SQLite connection sockets & schemas
│   ├── tracking.py      # Calorie logs, loops & telemetry algorithms
│   └── chat_engine.py   # RAG pipeline loops & Gemini sessions
└── frontend/
    ├── __init__.py
    ├── api_client.py    # Standardized Requests mapping endpoints
    ├── charts.py        # Matplotlib donut gauges & macro split charts
    ├── tab_chat.py      # Conversational view & quick-log buttons
    └── tab_logs.py      # Ingestion history grid list & scale modals
"""