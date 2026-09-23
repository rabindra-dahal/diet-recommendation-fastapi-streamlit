"""Automated unit test suite checking FastAPI operational endpoint states."""

from fastapi.testclient import TestClient
from main_backend import app

client = TestClient(app)


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
