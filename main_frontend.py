"""Main setup entry mapping parameters from client components to active display workspaces tabs."""

import streamlit as st
from frontend import api_client, charts, tab_chat, tab_logs

# 1. Fetch live metrics parameters right on loop boot execution
try:
    metrics = api_client.get_system_telemetry_metrics()
    history = api_client.get_conversational_history()
    foods = api_client.get_tracked_foods_list()
except Exception:
    st.error("🚨 Frontend application failed connecting to backend endpoint sockets! Please start `main_backend.py` first.")
    st.stop()

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.title("⚙️ Health Control")
    st.metric(label="🔑 Gemini API Calls Trace", value=f"{metrics['api_calls']} calls")
    st.markdown("---")
    
    st.write("💧 **Live Hydration Log**")
    st.metric(label="Daily Fluid Progress", value=f"{metrics['total_water']} ml / 2500 ml")
    c_w1, c_w2 = st.columns(2)
    if c_w1.button("➕ 250ml", width="stretch"):
        api_client.post_water_increment(250)
        st.rerun()
    if c_w2.button("➕ 500ml", width="stretch"):
        api_client.post_water_increment(500)
        st.rerun()
        
    st.markdown("---")
    active_program = st.selectbox("Target Dietary Focus Strategy:", ["Weight Loss", "Keto / Low-Carb", "Mass Gain", "High-Protein / Athletic"], key="ui_sb_strat")
    restrictions = st.multiselect("Allergies & Restrictions:", ["Gluten-Free", "Dairy-Free", "Nut-Free", "Vegan"], key="ui_sb_restrict")
    daily_kcal_cap = st.slider("Daily Calorie Intake Limit Target (kcal):", 1200, 4500, 2000, 50)
    
    if st.button("🚨 Reset Profile Session", type="primary", width="stretch"):
        api_client.post_system_reset_signal()
        st.rerun()

st.title("🥗 Modular GenAI Diet & Nutrition Platform Layer")
st.caption("Decoupled Frontend Interface tying into separate backend API services")

tab_ui_chat, tab_ui_logs = st.tabs(["💬 Dynamic Nutrition Chat Engine", "📊 My Macro Logs & Analytics Dashboards"])

with tab_ui_logs:
    st.write("### 📊 My Nutritional Analytics Dashboard")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric(label="🍽️ Total Logged Items", value=f"{metrics['total_saved']} items")
    col_kpi2.metric(label="🔥 Current Calorie Count", value=f"{metrics['total_calories']} kcal consumed")
    col_kpi3.metric(label="💧 Hydration Milestone Score", value=f"{metrics['total_water']} ml")
    
    st.markdown("---")
    charts.draw_analytics_dashboard_graphics(metrics, daily_kcal_cap)
    
    st.markdown("---")
    tab_logs.render_logs_and_rescaler_workspace(metrics, foods)

with tab_ui_chat:
    tab_chat.render_chat_workspace(history, active_program, restrictions, daily_kcal_cap)
