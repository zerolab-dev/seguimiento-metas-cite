import streamlit as st
import os

def apply_custom_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        .block-container { padding-top: 1.5rem; padding-bottom: 2.5rem; max-width: 96%; }
        .header-banner { background: linear-gradient(135deg, #1B365D 0%, #0F2C59 100%); color: #FFF; padding: 1.25rem 1.75rem; border-radius: 12px; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; }
        .header-title-box h1 { color: #FFF !important; font-size: 1.6rem !important; font-weight: 700 !important; margin: 0 !important; }
        .header-title-box p { color: #CBD5E1 !important; font-size: 0.9rem !important; margin: 0.25rem 0 0 0 !important; }
        .filter-section { background-color: #FFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; }
        .kpi-card { background-color: #FFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.1rem; text-align: left; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
        .kpi-label { font-size: 0.82rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 0.35rem; }
        .kpi-value { font-size: 1.65rem; font-weight: 700; color: #0F172A; }
        .kpi-subtext { font-size: 0.78rem; color: #64748B; margin-top: 0.35rem; }
        .kpi-badge-positive { background-color: #DCFCE7; color: #166534; padding: 0.15rem 0.5rem; border-radius: 9999px; font-weight: 600; font-size: 0.75rem; }
        .kpi-badge-negative { background-color: #FEE2E2; color: #991B1B; padding: 0.15rem 0.5rem; border-radius: 9999px; font-weight: 600; font-size: 0.75rem; }
        .footer-box { background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 1.25rem; margin-top: 2.5rem; border-radius: 8px; font-size: 0.82rem; color: #64748B; text-align: center; }
        .footer-warning { color: #C2410C; font-weight: 600; margin-top: 0.4rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header(logo_path="assets/logo_itp.png"):
    st.markdown(
        """
        <div class="header-banner">
            <div class="header-title-box">
                <h1>Seguimiento de Metas – Red CITE Pública</h1>
                <p>Consulta y análisis del avance de servicios y unidades productivas (UP)</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi_card(title, value, subtext="", badge_type="neutral"):
    badge_html = ""
    if badge_type == "positive":
        badge_html = f'<span class="kpi-badge-positive">{subtext}</span>'
    elif badge_type == "negative":
        badge_html = f'<span class="kpi-badge-negative">{subtext}</span>'
    elif subtext:
        badge_html = f'<div class="kpi-subtext">{subtext}</div>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_footer(selected_year, last_mod_time):
    st.markdown(
        f"""
        <div class="footer-box">
            <div><strong>Fuente de datos:</strong> Metas {selected_year} | Ejecución {selected_year}</div>
            <div><strong>Última actualización del archivo de ejecución:</strong> {last_mod_time}</div>
            <div class="footer-warning">
                ⚠️ Las categorías presupuestales son universos independientes y no deben sumarse entre sí.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
