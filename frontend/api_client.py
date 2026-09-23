"""Module abstracting standard REST operations away from UI layout blocks."""

import requests

BACKEND_URL = "http://127.0.0.1:8000"


def get_system_telemetry_metrics() -> dict:
    return requests.get(f"{BACKEND_URL}/api/tracker/metrics").json()


def get_conversational_history() -> list[dict]:
    return requests.get(f"{BACKEND_URL}/api/chat/history").json()


def get_tracked_foods_list() -> list[dict]:
    return requests.get(f"{BACKEND_URL}/api/tracker/foods").json()


def post_water_increment(ml: int) -> None:
    requests.post(f"{BACKEND_URL}/api/tracker/water", json={"amount_ml": ml})


def post_logged_food_item(name: str, cals: int, notes: str) -> None:
    requests.post(f"{BACKEND_URL}/api/tracker/foods", json={"item_name": name, "calories": cals, "entry_notes": notes})


def post_system_reset_signal() -> None:
    requests.post(f"{BACKEND_URL}/api/tracker/reset")

def post_bodyweight_update(weight_lbs_or_kg: float) -> None:
    """Dispatches user weight metrics down to the backend database service endpoints."""
    requests.post(f"{BACKEND_URL}/api/tracker/weight", json={"weight": weight_lbs_or_kg})

