"""Automated unit and integration test suite validating FastAPI operational endpoint states."""

import pytest
from fastapi.testclient import TestClient
from main_backend import app
from backend.db_core import init_db

# Instantiate the test client wrapper mapping your core application
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_database_schema():
    """Automated fixture running before every test execution pass to ensure schema initialization."""
    # ─── FIXED: EXPLICITLY INITIALIZE THE SQLITE SCHEMAS FOR THE CI ENVIRONMENT ───
    init_db()
    yield # Let the test assertions execute cleanly inside an initialized data layer


def test_database_kpi_metrics_endpoint():
    """Validates that the metrics engine yields correctly formatted baseline dictionary payloads."""
    response = client.get("/api/tracker/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_saved" in data
    assert "total_calories" in data
    assert "protein" in data
    assert "api_calls" in data


def test_logged_foods_retrieval_endpoint():
    """Ensures the core food logs sheet returns a structural array list layout."""
    response = client.get("/api/tracker/foods")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
