"""Central application hub exposing isolated endpoints to drive modular operations maps."""

import sqlite3
import json
from fastapi import FastAPI
from backend.db_core import init_db, get_db_connection
from backend.config import client
from backend import tracking, chat_engine

# Run baseline structural blueprints check on system startup
init_db()

app = FastAPI(title="Modular Nutrition Decoupled REST Core", version="2.5")


@app.post("/api/chat")
def process_chat(query: chat_engine.ChatQuery):
    tracking.add_api_telemetry_event("FastAPI Ingestion / Chat Inference")
    return chat_engine.query_gemini_with_rag(query)


@app.get("/api/chat/history")
def fetch_history():
    conn = get_db_connection()
    rows = conn.cursor().execute("SELECT role, content FROM chat_history ORDER BY id ASC").fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]


@app.get("/api/tracker/foods")
def list_foods():
    return tracking.get_logged_foods_list()


@app.post("/api/tracker/foods")
def save_food(food: tracking.FoodItem):
    tracking.save_or_update_food(food)
    return {"status": "success"}


@app.post("/api/tracker/water")
def log_water_metrics(water: tracking.WaterIntake):
    tracking.record_water(water)
    return {"status": "success"}


@app.get("/api/tracker/metrics")
def get_metrics_dashboard_values():
    return tracking.calculate_kpi_summary()


@app.post("/api/tracker/reset")
def execute_system_purge():
    tracking.purge_entire_session()
    return {"status": "cleared"}


@app.on_event("startup")
def verify_and_seed_knowledge_base():
    """Validates baseline values and calls batch embedding routines if table rows sit empty."""
    conn = get_db_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM food_knowledge_base").fetchone()
    if count == 0:
        catalog = [
            {"name": "Mediterranean Quinoa Bowl", "cat": "Weight Loss", "macros": "420 kcal, P:22g, C:45g, F:14g", "ing": "Quinoa, tomatoes, light feta."},
            {"name": "High-Protein Salmon Salad", "cat": "Keto / Low-Carb", "macros": "550 kcal, P:38g, C:8g, F:40g", "ing": "Salmon, baked avocado salad."}
        ]
        for b in catalog:
            emb = client.models.embed_content(model="gemini-embedding-001", contents=f"{b['name']} {b['cat']} {b['macros']}")
            conn.cursor().execute(
                "INSERT INTO food_knowledge_base (recipe_name, category, macro_profile, ingredients, embedding_json) VALUES (?, ?, ?, ?, ?)",
                (b["name"], b["cat"], b["macros"], b["ing"], json.dumps(emb.embeddings.values))
            )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_backend:app", host="127.0.0.1", port=8000, reload=True)
