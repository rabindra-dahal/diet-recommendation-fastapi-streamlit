"""Module rendering active chat conversation inputs and parsing automated header tracking links."""

import re
import requests
import streamlit as st
from frontend.api_client import BACKEND_URL, post_logged_food_item


def render_chat_workspace(chat_history: list, active_program: str, restrictions: list, daily_kcal_cap: int) -> None:
    """Loops through historical response strings and builds dynamic meal ingestion options handles."""
    for idx, msg in enumerate(chat_history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Intercept custom header pattern lines to render tracking buttons
            meal_blocks = []
            for line in msg["content"].split("\n"):
                clean_line = line.strip()
                
                # Regex safely extracts data even if Gemini includes markdown bolding like: "### 🍳 **Meal [Macros]**"
                if clean_line.startswith("### 🍳"):
                    # Strip out Markdown syntax tags and asterisks cleanly
                    normalized_line = re.sub(r"### 🍳\s*\*?\*?", "", clean_line).replace("**", "").strip()
                    
                    if "[" in normalized_line and "]" in normalized_line:
                        try:
                            # Isolate the food item name from the bracket text payload
                            display_name = normalized_line.split("[")[0].strip()
                            macro_bracket = normalized_line.split("[")[1].split("]")[0].strip()
                            
                            # Standardize macro tags matching database schema rules: "P:40g, C:60g, F:8g"
                            m_notes = ", ".join([t.strip() for t in macro_bracket.split(",") if "kcal" not in t.lower()]).strip()
                            
                            # Safely extract numerical calorie counts via sub-regex sweeps
                            calories = 0
                            for token in macro_bracket.replace(" ", "").split(","):
                                if token.lower().startswith("kcal:"):
                                    num_match = re.search(r"\d+", token)
                                    if num_match:
                                        calories = int(num_match.group())
                                        
                            meal_blocks.append({"name": display_name, "cals": calories, "notes": m_notes})
                        except Exception:
                            pass
                            
            if meal_blocks and msg["role"] == "assistant":
                st.caption("✨ **Automated One-Click Tracking Ledger Mapped:**")
                cols = st.columns(len(meal_blocks))
                for b_idx, meal in enumerate(meal_blocks):
                    with cols[b_idx]:
                        # FIXED: Guaranteed unique component signature keys to prevent registry collisions
                        if st.button(f"📥 Log: {meal['name']} ({meal['cals']} kcal)", key=f"chat_auto_btn_{idx}_{b_idx}", width="stretch"):
                            post_logged_food_item(meal["name"], meal["cals"], meal["notes"])
                            st.toast(f"FastAPI router parsed ingestion: Added {meal['name']}! 🚀")
                            st.rerun()

    if user_query := st.chat_input("Submit diet, workout, or macro profile questions here..."):
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.spinner("Processing request through FastAPI pipelines..."):
            payload = {"user_input": user_query, "active_program": active_program, "restrictions": restrictions, "daily_kcal_cap": daily_kcal_cap}
            response_obj = requests.post(f"{BACKEND_URL}/api/chat", json=payload)
            
            # Defensive guard clause to block non-JSON frontend crashes
            if response_obj.status_code != 200:
                st.error(f"⚠️ FastAPI Backend Server returned an unhandled error code: {response_obj.status_code}")
                st.stop()
                
            res = response_obj.json()
            if res.get("rag_meta"):
                st.info(f"🎯 **RAG Match Trace Confirmed by API** (Similarity Score: {res['rag_meta']['score']:.2f})")
            st.rerun()
