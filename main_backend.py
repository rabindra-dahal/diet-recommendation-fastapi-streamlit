"""Central application hub exposing isolated endpoints to drive modular operations maps."""

import json
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from backend.config import client
from backend.db_core import init_db, get_db_connection
from backend import tracking, chat_engine


# --- MODERN LINT-COMPLIANT LIFESPAN MANAGEMENT SYSTEM ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Orchestrates system setup baseline schemas and batch vector seeding on server startup."""
    # 1. Run structural blueprint table checks smoothly
    init_db()
    
    # 2. Execute automated vector knowledge base database seeding routine maps
    conn = get_db_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM food_knowledge_base").fetchone()
    
    if count == 0:
        print("🚀 Initializing lint-compliant system database seeding sequence...")
        catalog = [
            {"name": "Mediterranean Quinoa Bowl", "cat": "Weight Loss", "macros": "420 kcal, P:22g, C:45g, F:14g", "ing": "Quinoa, tomatoes, light feta."},
            {"name": "High-Protein Salmon Salad", "cat": "Keto / Low-Carb", "macros": "550 kcal, P:38g, C:8g, F:40g", "ing": "Salmon, baked avocado salad."}
        ]
        
        try:
            for b in catalog:
                text_content = f"{b['name']} {b['cat']} {b['macros']}"
                # Request a vector signature footprint tracking payload via Gemini API
                emb = client.models.embed_content(model="gemini-embedding-001", contents=text_content)
                
                if emb.embeddings:
                    # LINT FIXED: Explicitly pull index 0 values to conform with static type analyzers
                    raw_vector_array = emb.embeddings[0].values
                    
                    conn.cursor().execute(
                        """INSERT INTO food_knowledge_base 
                           (recipe_name, category, macro_profile, ingredients, embedding_json) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (b["name"], b["cat"], b["macros"], b["ing"], json.dumps(raw_vector_array))
                    )
            conn.commit()
            print("✅ Database successfully populated with initial RAG vector library data!")
        except Exception as e:
            print(f"❌ Structural database initialization vector failure: {str(e)}")
            
    conn.close()
    yield  # Separates the server startup lifecycle phase from the shutdown block phase cleanly


# Initialize core orchestration engine registering the modern lifespan lifecycle hook
app = FastAPI(title="Modular Nutrition Decoupled REST Core", version="2.5", lifespan=lifespan)


# --- DATA TRANSPORT TRANSFER SCHEMAS ---
class WeightLog(BaseModel):
    weight: float


# --- CORE ROUTING SERVICES REST ENDPOINTS ---
@app.post("/api/chat")
def process_chat(query: chat_engine.ChatQuery):
    """Routes dialog string parameters down into RAG pipelines and returns conversational replies."""
    tracking.add_api_telemetry_event("FastAPI Ingestion / Chat Inference")
    return chat_engine.query_gemini_with_rag(query)


@app.get("/api/chat/history")
def fetch_history():
    """Retrieves chronological text sequences stored inside chat history databases tables."""
    conn = get_db_connection()
    rows = conn.cursor().execute("SELECT role, content FROM chat_history ORDER BY id ASC").fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]


@app.get("/api/tracker/foods")
def list_foods():
    """Returns a json structured response list reflecting daily consumption ingestion blocks."""
    return tracking.get_logged_foods_list()


@app.post("/api/tracker/foods")
def save_food(food: tracking.FoodItem):
    """Persists or overwrites individual calorie trackers parameters in SQLite."""
    tracking.save_or_update_food(food)
    return {"status": "success"}


@app.post("/api/tracker/water")
def log_water_metrics(water: tracking.WaterIntake):
    """Appends hydration metric logs securely mapped to the active logging timestamp."""
    tracking.record_water(water)
    return {"status": "success"}


@app.post("/api/tracker/weight")
def log_user_weight(data: WeightLog):
    """Saves user bodyweight check-in snapshots to compile tracking progression line charts."""
    from datetime import datetime
    conn = get_db_connection()
    conn.cursor().execute(
        "INSERT OR REPLACE INTO health_goal_logs (log_date, weight_target) VALUES (?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), data.weight),
    )
    conn.commit()
    conn.close()
    return {"status": "success"}


@app.get("/api/tracker/metrics")
def get_metrics_dashboard_values():
    """Aggregates logged records and returns cumulative macro statistics and historical logs."""
    return tracking.calculate_kpi_summary()


@app.post("/api/tracker/reset")
def execute_system_purge():
    """Wipes active session chat lines, tracking telemetry counts, and fluid logs."""
    tracking.purge_entire_session()
    return {"status": "cleared"}


# --- DATABASE UTILITIES INSPECTION CHANNELS ---
@app.get("/api/db/tables")
def list_sqlite_tables():
    """Retrieves all registered active user storage table names from master schema rows."""
    conn = get_db_connection()
    cursor = conn.cursor()
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    ).fetchall()
    conn.close()
    return [t[0] for t in tables]


@app.get("/api/db/table/{table_name}")
def fetch_raw_table_rows(table_name: str):
    """Fetches every column and row entry within a requested database table dynamically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Sanitize parameter query strings slightly against malicious Injection tokens
        if not table_name.isalnum() and "_" not in table_name:
            return {"error": "Invalid structural layer table selection query string identifier."}
            
        data_rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        column_headers = [desc[0] for desc in cursor.description]
        conn.close()
        return {"columns": column_headers, "data": data_rows}
    except Exception as err:
        conn.close()
        return {"error": str(err)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_backend:app", host="127.0.0.1", port=8000, reload=True)
