"""Module organizing cosine similarity vector lookups and Gemini system prompting chains."""

import json
import numpy as np
from pydantic import BaseModel
from google.genai import types
from backend.config import client
from backend.db_core import get_db_connection


class ChatQuery(BaseModel):
    user_input: str
    active_program: str
    restrictions: list[str]
    daily_kcal_cap: int


def execute_vector_rag_lookup(user_input: str) -> Optional[dict]:
    """Runs a fast cosine match sweep across indexed recipe text tables."""
    try:
        emb_resp = client.models.embed_content(model="gemini-embedding-001", contents=user_input)
        q_emb = emb_resp.embeddings.values if emb_resp.embeddings else None
        
        if q_emb:
            conn = get_db_connection()
            rows = conn.cursor().execute(
                "SELECT recipe_name, category, macro_profile, ingredients, embedding_json FROM food_knowledge_base"
            ).fetchall()
            conn.close()
            
            if not rows:
                return None
                
            q_vec = np.array(q_emb)
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                return None
                
            results = []
            for name, cat, macros, ing, emb_json in rows:
                if not emb_json:
                    continue
                b_vec = np.array(json.loads(emb_json))
                b_norm = np.linalg.norm(b_vec)
                if b_norm == 0:
                    continue
                similarity = np.dot(q_vec, b_vec) / (q_norm * b_norm)
                results.append((similarity, {"title": name, "category": cat, "macros": macros, "ingredients": ing}))
                
            results.sort(key=lambda x: x, reverse=True)
            if results and results > 0.4:
                return {"score": float(results), **results}
    except Exception:
        pass
    return None


def query_gemini_with_rag(query: ChatQuery) -> dict:
    """Assembles chronological dialogue history and streams an instructional response match."""
    conn = get_db_connection()
    
    # Extract RAG profile matrix values
    rag_meta = execute_vector_rag_lookup(query.user_input)
    rag_context = json.dumps(rag_meta) if rag_meta else "[]"
    
    # Map context loops
    rows_hist = conn.cursor().execute("SELECT role, content FROM chat_history ORDER BY id ASC").fetchall()
    history_instances = [
        types.Content(role="model" if r == "assistant" else r, parts=[types.Part.from_text(text=c)])
        for r, c in rows_hist
    ]
    
    sys_ins = (
        f"You are an expert clinical dietician and athletic wellness coach.\n"
        f"Active Strategy: {query.active_program}. Strict Allergies/Restrictions: {', '.join(query.restrictions)}. Target Cap: {query.daily_kcal_cap} kcal.\n"
        f"Verified database recipe asset match context payload: {rag_context}.\n"
        "Provide highly personalized dietary choices. You MUST format meal selections inside markdown and start each "
        "recommendation item block line with a 3rd-level header matching EXACTLY this bracket pattern signature format: "
        "'### 🍳 [Meal Name] [P:[X]g, C:[Y]g, F:[Z]g, Kcal:[W]]' where X, Y, Z, W are exact numerical values calculated by you. "
        "Never leave out the bracket configuration block. Follow that header with bulleted macro stats and reasons. Respond immediately."
    )
    
    chat_session = client.chats.create(model="gemini-2.5-flash", history=history_instances)
    response = chat_session.send_message(message=query.user_input, config=types.GenerateContentConfig(system_instruction=sys_ins, temperature=0.3))
    
    # Save conversation details to the log table
    conn.cursor().execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", ("user", query.user_input))
    conn.cursor().execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", ("assistant", response.text))
    conn.commit()
    conn.close()
    
    return {"response": response.text, "rag_meta": rag_meta}
