"""Module containing presentation canvas dashboard generation rendering utilities."""

import matplotlib.pyplot as plt
import streamlit as st


def draw_analytics_dashboard_graphics(metrics: dict, target_cap: int) -> None:
    """Generates side-by-side goal completion rings and macronutrient split percentage indicators."""
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.write("🎯 **Calorie Intake Ring Gauge**")
        fig, ax = plt.subplots(figsize=(3, 3))
        rem = max(0, target_cap - metrics["total_calories"])
        ax.pie([metrics["total_calories"], rem], colors=['#d62728', '#e0e0e0'], startangle=90, counterclock=False, wedgeprops=dict(width=0.3, edgecolor='white'))
        ax.text(0, 0, f"{metrics['total_calories']}/{target_cap}\nkcal", ha='center', va='center', fontsize=10, fontweight='bold')
        st.pyplot(fig)
        plt.close()
        
    with c_right:
        st.write("📊 **Macronutrient Balance Split**")
        p, c, f = metrics["protein"], metrics["carbs"], metrics["fats"]
        if p == 0 and c == 0 and f == 0:
            st.info("Log meals using quick action options to generate interactive macro ratio distribution curves.")
        else:
            fig, ax = plt.subplots(figsize=(3, 3))
            ax.pie([p * 4, c * 4, f * 9], labels=[f"P ({p}g)", f"C ({c}g)", f"F ({f}g)"], colors=['#1f77b4', '#9467bd', '#bcbd22'], autopct='%1.1f%%')
            st.pyplot(fig)
            plt.close()
