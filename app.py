import streamlit as st
import pandas as pd
from utils.styles import apply_custom_styles, render_header, render_kpi_card, render_footer
from utils.data_loader import get_available_years, get_file_modification_time, load_year_data
from utils.data_processing import (
    MONTHS_SPANISH, validate_and_prep_dataset, get_filter_options, filter_dataset
)
from utils.calculations import compute_kpis, generate_pivot_summary_table
from utils.charts import (
    create_monthly_evolution_chart, create_distribution_chart,
    create_top_ranking_chart, create_complexity_chart
)
from utils.excel_export import generate_excel_download

st.set_page_config(
    page_title="Seguimiento de Metas – Red CITE Pública",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_styles()
available_years = get_available_years()

if not available_years:
    st.error("🚨 No se encontraron pares de archivos de datos en la carpeta `data/`.")
    st.info("Para utilizar la aplicación, por favor asegura colocar en `data/`: `meta_2026.xlsx` y `ejecucion_2026.xlsx`")
    st.stop()

render_header()

st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.subheader("🔍 Filtros de Consulta")

col_year, col_ind, col_cat, col_cite = st.columns([1, 1.3, 1.7, 2])

with col_year:
    selected_year = st.selectbox("Año", options=available_years, index=len(available_years)-1)

with col_ind:
    indicator = st.selectbox(
        "Indicador",
        options=["Servicios", "Unidades productivas (UP)"],
        help="En PP0094 representa acuicultores. En PP0095 representa agentes de la pesca artesanal."
    )

try:
    raw_data = load_year_data(selected_year)
    if indicator == "Servicios":
        dataset_long = validate_and_prep_dataset(raw_data['meta_servicios'], raw_data['ejecucion_servicios'], "Servicios")
    else:
        dataset_long = validate_and_prep_dataset(raw_data['meta_up'], raw_data['ejecucion_up'], "Unidades productivas (UP)")
except Exception as e:
    st.error(f"❌ Error al procesar los datos: {str(e)}")
    st.stop()

filter_opts = get_filter_options(dataset_long)

with col_cat:
    selected_cat = st.selectbox(
        "Categoría Presupuestal *",
        options=filter_opts['categories'],
        help="Las categorías presupuestales son universos independientes y no deben sumarse."
    )

filter_opts = get_filter_options(dataset_long, current_cat=selected_cat)

with col_cite:
    selected_cite = st.selectbox(
        "CITE / Entidad",
        options=filter_opts['cites'],
        help="'ITP red CITE públicos' representa directamente el Total Nacional."
    )

col_m_start, col_m_end, col_f1, col_f2, col_f3 = st.columns([1, 1, 1.2, 1.4, 1.2])

with col_m_start:
    start_month = st.selectbox("Mes Inicio", options=MONTHS_SPANISH, index=0)

with col_m_end:
    end_month = st.selectbox("Mes Fin", options=MONTHS_SPANISH, index=11)

start_idx = MONTHS_SPANISH.index(start_month)
end_idx = MONTHS_SPANISH.index(end_month)

if end_idx < start_idx:
    st.warning("⚠️ El Mes Fin debe ser mayor o igual al Mes Inicio. Ajustando consulta...")
    end_month = start_month
    end_idx = start_idx

selected_service_type = "Todos"
selected_task = "Todas"
selected_complexity = "Todas"

if indicator == "Servicios":
    filter_opts_cascade = get_filter_options(dataset_long, current_cat=selected_cat)
    with col_f1:
        selected_service_type = st.selectbox("Tipo de Servicio", options=filter_opts_cascade['service_types'])

    filter_opts_cascade = get_filter_options(dataset_long, current_cat=selected_cat, current_type=selected_service_type)
    with col_f2:
        selected_task = st.selectbox("Tarea", options=filter_opts_cascade['tasks'])

    filter_opts_cascade = get_filter_options(dataset_long, current_cat=selected_cat, current_type=selected_service_type, current_task=selected_task)
    with col_f3:
        selected_complexity = st.selectbox("Complejidad", options=filter_opts_cascade['complexities'])
else:
    with col_f1:
        st.text_input("Tipo de Servicio", value="No aplica", disabled=True)
    with col_f2:
        st.text_input("Tarea", value="No aplica", disabled=True)
    with col_f3:
        st.text_input("Complejidad", value="No aplica", disabled=True)

st.markdown('</div>', unsafe_allow_html=True)

df_filtered = filter_dataset(
    dataset_long,
    category=selected_cat,
    cite=selected_cite,
    service_type=selected_service_type,
    task=selected_task,
    complexity=selected_complexity
)

kpis = compute_kpis(df_filtered, start_month, end_month)

st.subheader("📈 Indicadores Clave del Periodo")
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    render_kpi_card("Meta del Periodo", f"{kpis['meta_periodo']:,.0f}", f"Periodo: {kpis['period_label']}")
with kpi_col2:
    render_kpi_card("Ejecutado Periodo", f"{kpis['ejec_periodo']:,.0f}", f"Meta Anual: {kpis['meta_anual']:,.0f}")
with kpi_col3:
    avance_val = kpis['avance_periodo']
    badge_type = "positive" if avance_val >= 100 else ("negative" if avance_val < 75 else "neutral")
    render_kpi_card("% Avance Periodo", f"{avance_val:.1f}%", f"Avance Anual: {kpis['avance_anual']:.1f}%", badge_type=badge_type)
with kpi_col4:
    brecha = kpis['brecha_periodo']
    badge_type = "positive" if brecha >= 0 else "negative"
    sign = "+" if brecha > 0 else ""
    render_kpi_card("Brecha del Periodo", f"{sign}{brecha:,.0f}", "Ejecutado - Meta", badge_type=badge_type)
with kpi_col5:
    render_kpi_card("Meses Considerados", f"{kpis['num_months_period']} de 12", kpis['period_label'])

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Análisis Gráfico")

chart_row1_col1, chart_row1_col2 = st.columns([1.6, 1])

with chart_row1_col1:
    fig_evol = create_monthly_evolution_chart(df_filtered, start_month, end_month)
    st.plotly_chart(fig_evol, use_container_width=True)

with chart_row1_col2:
    start_num = MONTHS_SPANISH.index(start_month) + 1
    end_num = MONTHS_SPANISH.index(end_month) + 1
    df_period_only = df_filtered[(df_filtered['Mes_Num'] >= start_num) & (df_filtered['Mes_Num'] <= end_num)]
    fig_dist = create_distribution_chart(df_period_only, selected_type=selected_service_type)
    st.plotly_chart(fig_dist, use_container_width=True)

if indicator == "Servicios":
    chart_row2_col1, chart_row2_col2 = st.columns(2)
    with chart_row2_col1:
        fig_rank = create_top_ranking_chart(df_period_only)
        if fig_rank:
            st.plotly_chart(fig_rank, use_container_width=True)
    with chart_row2_col2:
        fig_comp = create_complexity_chart(df_period_only)
        if fig_comp:
            st.plotly_chart(fig_comp, use_container_width=True)

st.subheader("📋 Tabla Detalle Mes a Mes")
col_desag, col_space, col_dl = st.columns([1.5, 2, 1.2])

with col_desag:
    desag_options = ["Tipo de servicio", "Nombre de tarea", "Nivel de complejidad", "Sin desagregar"] if indicator == "Servicios" else ["CITE/UT", "Sin desagregar"]
    selected_drill = st.selectbox("Desagregar por:", options=desag_options, index=0)

pivot_summary = generate_pivot_summary_table(df_filtered, selected_drill, start_month, end_month)

filters_payload = {
    'Año': selected_year,
    'Indicador': indicator,
    'Categoría presupuestal': selected_cat,
    'CITE/UT': selected_cite,
    'Mes de inicio': start_month,
    'Mes de fin': end_month,
    'Tipo servicio': selected_service_type,
    'Tarea': selected_task,
    'Complejidad': selected_complexity
}

excel_bytes = generate_excel_download(pivot_summary, kpis, filters_payload)

with col_dl:
    st.markdown("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Descargar en Excel",
        data=excel_bytes,
        file_name=f"Seguimiento_Metas_{selected_year}_{indicator.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

if not pivot_summary.empty:
    display_df = pivot_summary.copy()
    col_renames = {f"{m}_Meta": f"{m[:3]} Meta" for m in MONTHS_SPANISH}
    col_renames.update({f"{m}_Ejec": f"{m[:3]} Ejec" for m in MONTHS_SPANISH})
    col_renames.update({
        'Meta_Periodo': 'Meta Periodo',
        'Ejec_Periodo': 'Ejec. Periodo',
        'Avance_Periodo': '% Avance Periodo',
        'Meta_Anual': 'Meta Anual',
        'Ejec_Anual': 'Ejec. Anual',
        'Avance_Anual': '% Avance Anual'
    })
    display_df.rename(columns=col_renames, inplace=True)

    format_dict = {col: ("{:.1f}%" if '% Avance' in col else "{:,.0f}") for col in display_df.columns if col != 'Detalle'}
    st.dataframe(display_df.style.format(format_dict), use_container_width=True, hide_index=True, height=400)
else:
    st.info("No hay registros que coincidan con los filtros seleccionados.")

last_mod = get_file_modification_time(selected_year)
render_footer(selected_year, last_mod)
