import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_processing import MONTHS_SPANISH, MONTH_ABBR, MONTH_NUM

def create_monthly_evolution_chart(df, start_month, end_month):
    start_num, end_num = MONTH_NUM[start_month], MONTH_NUM[end_month]
    monthly = df.groupby(['Mes', 'Mes_Num'])[['Meta', 'Ejecutado']].sum().reset_index().sort_values('Mes_Num')

    full_m = pd.DataFrame({'Mes': MONTHS_SPANISH, 'Mes_Num': [MONTH_NUM[m] for m in MONTHS_SPANISH]})
    monthly = pd.merge(full_m, monthly, on=['Mes', 'Mes_Num'], how='left').fillna(0)

    colors_ejec = ["#0F2C59" if start_num <= r['Mes_Num'] <= end_num else "rgba(15, 44, 89, 0.35)" for _, r in monthly.iterrows()]
    colors_meta = ["#94A3B8" if start_num <= r['Mes_Num'] <= end_num else "rgba(148, 163, 184, 0.35)" for _, r in monthly.iterrows()]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=[MONTH_ABBR[m] for m in monthly['Mes']], y=monthly['Meta'], name='Meta', marker_color=colors_meta))
    fig.add_trace(go.Bar(x=[MONTH_ABBR[m] for m in monthly['Mes']], y=monthly['Ejecutado'], name='Ejecutado', marker_color=colors_ejec))

    fig.update_layout(
        title=dict(text=f"Evolución Mensual Meta vs. Ejecutado ({start_month} – {end_month})", font=dict(size=14, color="#1B365D")),
        barmode='group', plot_bgcolor="#FFF", paper_bgcolor="#FFF", margin=dict(l=20, r=20, t=40, b=30), height=340
    )
    return fig

def create_distribution_chart(df_period, selected_type="Todos"):
    if df_period.empty or df_period['Ejecutado'].sum() == 0:
        fig = go.Figure()
        fig.add_annotation(text="Sin datos de ejecución", showarrow=False)
        fig.update_layout(height=280)
        return fig

    group_col = 'Nombre de tarea' if selected_type != "Todos" and 'Nombre de tarea' in df_period.columns else ('Tipo de servicio' if 'Tipo de servicio' in df_period.columns else 'CITE/UT')
    dist = df_period.groupby(group_col)['Ejecutado'].sum().reset_index()
    dist = dist[dist['Ejecutado'] > 0]

    fig = go.Figure(data=[go.Pie(labels=dist[group_col], values=dist['Ejecutado'], hole=.45, textinfo='percent+label')])
    fig.update_layout(title=dict(text=f"Distribución por {group_col}", font=dict(size=14, color="#1B365D")), height=320, showlegend=False)
    return fig

def create_top_ranking_chart(df_period):
    if df_period.empty or 'Nombre de tarea' not in df_period.columns: return None
    top_tasks = df_period.groupby('Nombre de tarea')['Ejecutado'].sum().reset_index().sort_values('Ejecutado').tail(5)
    top_tasks = top_tasks[top_tasks['Ejecutado'] > 0]
    if top_tasks.empty: return None

    fig = go.Figure(go.Bar(x=top_tasks['Ejecutado'], y=top_tasks['Nombre de tarea'], orientation='h', marker_color="#10B981"))
    fig.update_layout(title=dict(text="Top 5 Tareas con Mayor Ejecución", font=dict(size=14, color="#1B365D")), height=320)
    return fig

def create_complexity_chart(df_period):
    if df_period.empty or 'Nivel de complejidad' not in df_period.columns: return None
    comp = df_period.groupby('Nivel de complejidad')['Ejecutado'].sum().reset_index()
    comp = comp[comp['Ejecutado'] > 0]
    if comp.empty: return None

    fig = go.Figure(go.Bar(x=comp['Nivel de complejidad'], y=comp['Ejecutado'], marker_color="#3B82F6"))
    fig.update_layout(title=dict(text="Ejecución por Nivel de Complejidad", font=dict(size=14, color="#1B365D")), height=320)
    return fig
