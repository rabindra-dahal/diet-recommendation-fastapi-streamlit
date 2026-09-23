"""Module orchestrating arithmetic calculations for telemetry statistics and logging tracks."""

import sqlite3
from datetime import datetime
from pydantic import BaseModel
from backend.db_core import get_db_connection


class FoodItem(BaseModel):
    item_name: str
    calories: int
    entry_notes: str


class WaterIntake(BaseModel):
    amount_ml: int


def add_api_telemetry_event(call_type: str) -> None:
    """Logs an internal component function runtime call event."""
    conn = get_db_connection()
    conn.cursor().execute(
        "INSERT INTO api_usage_telemetry (call_type, timestamp) VALUES (?, ?)",
        (call_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_logged_foods_list() -> list[dict]:
    """Retrieves all tracked meal objects using row unpacking fields."""
    conn = get_db_connection()
    rows = conn.cursor().execute(
        "SELECT id, item_name, calories, entry_notes FROM dynamic_food_log ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [
        {"id": f_id, "title": name, "calories": cals, "notes": notes}
        for f_id, name, cals, notes in rows
    ]


def save_or_update_food(food: FoodItem) -> None:
    """Writes explicit user meal options down to SQLite data grids."""
    conn = get_db_connection()
    conn.cursor().execute(
        """INSERT OR REPLACE INTO dynamic_food_log (item_name, calories, entry_notes) 
           VALUES (?, ?, ?)""",
        (food.item_name, food.calories, food.entry_notes),
    )
    conn.commit()
    conn.close()


def record_water(water: WaterIntake) -> None:
    """Appends fluid logs securely mapped to the active logging timestamp."""
    conn = get_db_connection()
    conn.cursor().execute(
        "INSERT INTO hydration_log (log_date, amount_ml) VALUES (?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), water.amount_ml),
    )
    conn.commit()
    conn.close()


def calculate_kpi_summary() -> dict:
    """Aggregates logged records and returns cumulative macro statistics and historical logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rows = cursor.execute("SELECT calories, entry_notes FROM dynamic_food_log").fetchall()
    total_saved = len(rows)
    total_calories = sum([r for r, _ in rows if r is not None])
    
    protein, carbs, fats = 0, 0, 0
    for _, notes in rows:
        if not notes:
            continue
        try:
            for part in notes.replace(" ", "").split(","):
                if part.startswith("P:") and "g" in part:
                    protein += int(part.split("P:").split("g"))
                elif part.startswith("C:") and "g" in part:
                    carbs += int(part.split("C:").split("g"))
                elif part.startswith("F:") and "g" in part:
                    fats += int(part.split("F:").split("g"))
        except Exception:
            pass
            
    water_res = cursor.execute(
        "SELECT SUM(amount_ml) FROM hydration_log WHERE log_date = ?",
        (datetime.now().strftime("%Y-%m-%d"),),
    ).fetchone()
    total_water = water_res if water_res and water_res is not None else 0
    
    api_res = cursor.execute("SELECT COUNT(*) FROM api_usage_telemetry").fetchone()
    weight_rows = cursor.execute(
        "SELECT log_date, weight_target FROM health_goal_logs ORDER BY log_date ASC"
    ).fetchall()
    
    conn.close()
    return {
        "total_saved": total_saved,
        "total_calories": total_calories,
        "protein": protein,
        "carbs": carbs,
        "fats": fats,
        "total_water": total_water,
        "api_calls": api_res if api_res else 0,
        "weight_logs": weight_rows
    }


def purge_entire_session() -> None:
    """Wipes all rows across storage tables during full profile restarts."""
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM chat_history")
    conn.cursor().execute("DELETE FROM dynamic_food_log")
    conn.cursor().execute("DELETE FROM api_usage_telemetry")
    conn.cursor().execute("DELETE FROM hydration_log")
    conn.commit()
    conn.close()
