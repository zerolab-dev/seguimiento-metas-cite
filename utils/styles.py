import streamlit as st
import os
import base64


def apply_custom_styles():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1E293B;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 96%;
}

.header-banner {
    background: linear-gradient(135deg, #1B365D 0%, #0F2C59 100%);
    color: #FFFFFF;
    padding: 1.25rem 1.75rem;
    border-radius: 12px;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    min-height: 105px;
}

.header-logo-box {
    background: #FFFFFF;
    border-radius: 9px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
}

.header-logo {
    width: 145px;
    height: auto;
    display: block;
}

.header-title-box {
    min-width: 0;
}

.header-title-box h1 {
    color: #FFFFFF !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.header-title-box p {
    color: #D7E2F0 !important;
    font-size: 0.9rem !important;
    margin: 0.4rem 0 0 0 !important;
    padding: 0 !important;
}

.filter-section {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
}

.kpi-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    text-align: left;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.kpi-label {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #64748B;
    margin-bottom: 0.35rem;
}

.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #0F172A;
}

.kpi-subtext {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.35rem;
}

.kpi-badge-positive {
    background-color: #DCFCE7;
    color: #166534;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.75rem;
}

.kpi-badge-negative {
    background-color: #FEE2E2;
    color: #991B1B;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.75rem;
}

.footer-box {
    background-color: #F8FAFC;
    border-top: 1px solid #E2E8F0;
    padding: 1.25rem;
    margin-top: 2.5rem;
    border-radius: 8px;
    font-size: 0.82rem;
    color: #64748B;
    text-align: center;
}

.footer-warning {
    color: #C2410C;
    font-weight: 600;
    margin-top: 0.4rem;
}

@media (max-width: 800px) {
    .header-banner {
        align-items: flex-start;
        gap: 0.9rem;
        padding: 1rem;
    }

    .header-logo {
        width: 105px;
    }

    .header-title-box h1 {
        font-size: 1.22rem !important;
    }

    .header-title-box p {
        font-size: 0.78rem !important;
    }
}
</style>
""",
        unsafe_allow_html=True
    )


def render_header(logo_path="assets/logo_itp.png"):
    logo_html = ""

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode("utf-8")

        ext = os.path.splitext(logo_path)[1].lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

        logo_html = (
            '<div class="header-logo-box">'
            f'<img src="data:{mime};base64,{encoded_logo}" '
            'class="header-logo" alt="Logo ITP Red CITE">'
            '</div>'
        )

    html = (
        '<div class="header-banner">'
        f'{logo_html}'
        '<div class="header-title-box">'
        '<h1>Seguimiento de Metas – Red CITE Pública</h1>'
        '<p>Consulta y análisis del avance de servicios y unidades productivas (UP)</p>'
        '</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(title, value, subtext="", badge_type="neutral"):
    badge_html = ""
    if badge_type == "positive":
        badge_html = f'<span class="kpi-badge-positive">{subtext}</span>'
    elif badge_type == "negative":
        badge_html = f'<span class="kpi-badge-negative">{subtext}</span>'
    elif subtext:
        badge_html = f'<div class="kpi-subtext">{subtext}</div>'

    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{title}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{badge_html}'
        f'</div>',
        unsafe_allow_html=True
    )


def render_footer(selected_year, last_mod_time):
    st.markdown(
        f'<div class="footer-box">'
        f'<div><strong>Fuente de datos:</strong> Metas {selected_year} | Ejecución {selected_year}</div>'
        f'<div><strong>Última actualización del archivo de ejecución:</strong> {last_mod_time}</div>'
        f'<div class="footer-warning">⚠️ Las categorías presupuestales son universos independientes y no deben sumarse entre sí.</div>'
        f'</div>',
        unsafe_allow_html=True
    )
