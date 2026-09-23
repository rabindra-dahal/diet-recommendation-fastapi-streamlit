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
    init_db()
    yield  # Let the test assertions execute cleanly inside an initialized data layer


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


# ─── NEW: ADDITIONAL INTEGRATION TEST CASES ───

def test_save_food_entry_endpoint():
    """Validates that a new meal recommendation can be posted and successfully saved to the log."""
    food_payload = {
        "item_name": "Test Avocado Egg Toast",
        "calories": 350,
        "entry_notes": "P:18g, C:25g, F:20g"
    }
    response = client.post("/api/tracker/foods", json=food_payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify that the meal is now queryable in the tracking ledger list
    get_response = client.get("/api/tracker/foods")
    foods_list = get_response.json()
    assert any(item["title"] == "Test Avocado Egg Toast" for item in foods_list)


def test_log_water_metrics_endpoint():
    """Ensures hydration milestones increments post seamlessly to backend hydration tables."""
    water_payload = {"amount_ml": 250}
    response = client.post("/api/tracker/water", json=water_payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_log_user_weight_endpoint():
    """Validates that checking in bodyweight snapshots records successfully to data tables."""
    weight_payload = {"weight": 74.5}
    response = client.post("/api/tracker/weight", json=weight_payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_list_sqlite_tables_inspector_endpoint():
    """Verifies that the database master explorer correctly returns the schema structure."""
    response = client.get("/api/db/tables")
    assert response.status_code == 200
    
    tables_list = response.json()
    assert isinstance(tables_list, list)
    # Ensure standard structural blueprint tables exist in the registry array
    assert "dynamic_food_log" in tables_list
    assert "chat_history" in tables_list


def test_fetch_raw_table_rows_valid_and_invalid():
    """Checks data mapping extraction for valid parameters and verifies SQL Injection shielding."""
    # Test a valid table structure request
    response_valid = client.get("/api/db/table/dynamic_food_log")
    assert response_valid.status_code == 200
    assert "columns" in response_valid.json()
    assert "data" in response_valid.json()

    # Test an invalid/malicious query format string to check backend guards
    response_invalid = client.get("/api/db/table/drop_table;--")
    assert response_invalid.status_code == 200
    assert "error" in response_invalid.json()
