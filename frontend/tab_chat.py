"""Module rendering active chat conversation inputs and parsing automated header tracking links."""

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
                if line.strip().startswith("### 🍳"):
                    raw_h = line.replace("### 🍳", "").replace("**", "").replace("`", "").strip()
                    if "[" in raw_h and "]" in raw_h:
                        try:
                            d_name = raw_h.split("[").strip()
                            bracket = raw_h.split("[").split("]").strip()
                            calories = sum([int(t.lower().split("kcal:")) for t in bracket.replace(" ", "").split(",") if t.lower().startswith("kcal:")])
                            m_notes = ", ".join([t for t in bracket.split(",") if "kcal" not in t.lower()]).strip()
                            meal_blocks.append({"name": d_name, "cals": calories, "notes": m_notes})
                        except Exception:
                            pass
                            
            if meal_blocks and msg["role"] == "assistant":
                st.caption("✨ **Automated Fast-Track Loggers Mapped:**")
                cols = st.columns(len(meal_blocks))
                for b_idx, meal in enumerate(meal_blocks):
                    with cols[b_idx]:
                        if st.button(f"📥 Log: {meal['name']} ({meal['cals']} kcal)", key=f"c_btn_{idx}_{b_idx}", width="stretch"):
                            post_logged_food_item(meal["name"], meal["cals"], meal["notes"])
                            st.toast(f"Successfully logged {meal['name']} to backend tables!")
                            st.rerun()

    if user_query := st.chat_input("Submit diet, workout, or macro profile questions here..."):
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.spinner("Processing request through FastAPI pipelines..."):
            payload = {"user_input": user_query, "active_program": active_program, "restrictions": restrictions, "daily_kcal_cap": daily_kcal_cap}
            res = requests.post(f"{BACKEND_URL}/api/chat", json=payload).json()
            if res.get("rag_meta"):
                st.info(f"🎯 **RAG Match Trace Confirmed by API** (Similarity Score: {res['rag_meta']['score']:.2f})")
            st.rerun()
