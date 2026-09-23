"""UI Module presenting a granular raw table viewer for inspecting all SQLite storage layers via FastAPI."""

import streamlit as st
import pandas as pd
import requests

BACKEND_URL = "http://127.0.0.1:8000"


def render_database_tables_inspector() -> None:
    """Renders dataframes representing all underlying system database tables via REST endpoints."""
    st.markdown("---")
    st.write("### 🔍 System Database Table Inspector")
    st.caption("Inspect raw relational row metrics across all active storage schemas inside `health_tracker.db`.")

    try:
        # 1. Fetch available table schema names from backend registry channel
        tables_response = requests.get(f"{BACKEND_URL}/api/db/tables")
        if tables_response.status_code != 200:
            st.info("The backend database engine reports no tables active.")
            return
            
        table_names = tables_response.json()
        
        # 2. Render dropdown select box mapping individual table structures
        selected_table = st.selectbox(
            "Select Database Table to Inspect:",
            options=table_names,
            key="diet_db_inspector_table_select_dropdown"
        )

        if selected_table:
            # 3. Pull all raw metrics rows matching selection dynamically
            data_response = requests.get(f"{BACKEND_URL}/api/db/table/{selected_table}")
            
            if data_response.status_code == 200:
                table_payload = data_response.json()
                
                if "error" in table_payload:
                    st.error(f"Backend SQL Error: {table_payload['error']}")
                elif not table_payload.get("data"):
                    st.info(f"Table `{selected_table}` is currently empty (0 rows initialized).")
                else:
                    # 4. Map cleanly to a pandas DataFrame using exact headers
                    df = pd.DataFrame(
                        data=table_payload["data"], 
                        columns=table_payload["columns"]
                    )
                    
                    # Build an interactive data table representation frame
                    st.dataframe(df, width='stretch')
                    st.caption(f"Total Record Footprint Count: `{len(df)} rows` managed in `{selected_table}`.")
                    
    except Exception as err:
        st.error(f"Failed to read raw relational rows from endpoint socket: {str(err)}")
