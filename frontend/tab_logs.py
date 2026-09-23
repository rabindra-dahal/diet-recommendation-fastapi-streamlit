"""Module rendering numerical KPI callout summaries, saved histories list, and calculation modals."""

import streamlit as st
import pandas as pd
from frontend.api_client import post_logged_food_item


def render_logs_and_rescaler_workspace(metrics: dict, logged_foods: list) -> None:
    """Handles core ledger tables tracking and proportional multiplier updates calculations."""
    st.write("### 🥗 Daily Ingestion History List")
    
    if logged_foods:
        st.write("#### 📋 Raw Ledger Sheet Dataframe View")
        # ─── FIXED: UPDATED DATAFRAME LAYOUT PARAMETER ARGUMENT FOR CONTAINER EXPANSION ───
        st.dataframe(pd.DataFrame(logged_foods)[["title", "calories", "notes"]], width='stretch')
        st.markdown("---")

    if not logged_foods:
        st.info("Your logging sheets currently hold zero entries.")
        return

    for idx, food in enumerate(logged_foods):
        # Enforce consistent 3:1 width layout distribution ratios
        c_lbl, c_btn = st.columns([3, 1])
        
        with c_lbl:
            st.write(f"**{food['title']}** — `{food['calories']} kcal` | _{food['notes']}_")
        
        with c_btn:
            if st.button("✏️ Scale Macro", key=f"scale_f_btn_{idx}", width="stretch"):
                @st.dialog("📝 Proportional Multiplier Micro Adjuster Form")
                def run_modal(f_item=food):
                    st.write(f"Adjust calculations weights for: {f_item['title']}")
                    old_kcal = max(1, f_item['calories'])
                    
                    op, oc, of = 0, 0, 0
                    try:
                        # Clean up text tokens before breaking values apart
                        for token in f_item['notes'].replace(" ", "").split(","):
                            # CORRECT POSITION EXTRACT UNPACKING SIGNATURES
                            if token.startswith("P:") and "g" in token:
                                op = int(token.split("P:")[1].split("g")[0])
                            elif token.startswith("C:") and "g" in token:
                                oc = int(token.split("C:")[1].split("g")[0])
                            elif token.startswith("F:") and "g" in token:
                                of = int(token.split("F:")[1].split("g")[0])
                    except Exception as e:
                        st.error(f"Internal String Parser Conflict: {str(e)}")
                    
                    with st.form(key="scale_form_modal_instance", border=False):
                        new_kcal = st.number_input("New Calorie Level Target (kcal):", min_value=0, value=old_kcal, step=50)
                        
                        st.markdown(f"**Calculated Shift Preview:** P: {op}g ➔ {round(op * (new_kcal/old_kcal))}g | C: {oc}g ➔ {round(oc * (new_kcal/old_kcal))}g | F: {of}g ➔ {round(of * (new_kcal/old_kcal))}g")
                        
                        if st.form_submit_button("💾 Save Scaled Entry", width="stretch"):
                            multiplier = new_kcal / old_kcal
                            
                            # Build the updated macro string sequence to refresh your charts
                            updated_notes = f"P:{round(op * multiplier)}g, C:{round(oc * multiplier)}g, F:{round(of * multiplier)}g"
                            
                            # Dispatches the clean values directly down to your FastAPI container layers
                            post_logged_food_item(f_item['title'], new_kcal, updated_notes)
                            st.toast("Recalculation committed to backend storage layers! 🚀")
                            st.rerun()
                run_modal()
