"""Module rendering numerical KPI callout summaries, saved histories list, and calculation modals."""

import streamlit as st
import pandas as pd
from frontend.api_client import post_logged_food_item


def render_logs_and_rescaler_workspace(metrics: dict, logged_foods: list) -> None:
    """Handles core ledger tables tracking and proportional multiplier updates calculations."""
    st.write("### 🥗 Daily Ingestion History List")
    
    if logged_foods:
        st.write("#### 📋 Raw Ledger Sheet Dataframe View")
        st.dataframe(pd.DataFrame(logged_foods)[["title", "calories", "notes"]], use_container_width=True)
        st.markdown("---")

    if not logged_foods:
        st.info("Your logging sheets currently hold zero entries.")
        return

    for idx, food in enumerate(logged_foods):
        c_lbl, c_btn = st.columns()
        c_lbl.write(f"**{food['title']}** — `{food['calories']} kcal` | _{food['notes']}_")
        
        if c_btn.button("✏️ Scale Macro", key=f"scale_f_btn_{idx}", width="stretch"):
            @st.dialog("📝 Proportional Multiplier Micro Adjuster Form")
            def run_modal(f_item=food):
                st.write(f"Adjust calculations weights for: {f_item['title']}")
                old_kcal = max(1, f_item['calories'])
                
                op, oc, of = 0, 0, 0
                try:
                    for token in f_item['notes'].replace(" ", "").split(","):
                        if token.startswith("P:"): op = int(token.split("P:").split("g"))
                        elif token.startswith("C:"): oc = int(token.split("C:").split("g"))
                        elif token.startswith("F:"): of = int(token.split("F:").split("g"))
                except Exception:
                    pass
                
                with st.form(key="scale_form_modal_instance", border=False):
                    new_kcal = st.number_input("New Calorie Level Target (kcal):", min_value=0, value=old_kcal, step=50)
                    if st.form_submit_button("💾 Save Scaled Entry"):
                        multiplier = new_kcal / old_kcal
                        updated_notes = f"P:{round(op * multiplier)}g, C:{round(oc * multiplier)}g, F:{round(of * multiplier)}g"
                        post_logged_food_item(f_item['title'], new_kcal, updated_notes)
                        st.toast("Recalculation committed to backend storage layers!")
                        st.rerun()
            run_modal()
