import pandas as pd
from utils.data_processing import MONTHS_SPANISH, MONTH_NUM


def _pct(ejec, meta):
    return (ejec / meta * 100) if meta > 0 else 0.0


def compute_kpis(df, start_month, end_month):
    start_num, end_num = MONTH_NUM[start_month], MONTH_NUM[end_month]
    p = df[df['Mes_Num'].between(start_num, end_num)]
    meta_p, ejec_p = p['Meta'].sum(), p['Ejecutado'].sum()
    meta_a, ejec_a = df['Meta'].sum(), df['Ejecutado'].sum()
    return {
        'meta_periodo':meta_p, 'ejec_periodo':ejec_p, 'avance_periodo':_pct(ejec_p,meta_p),
        'brecha_periodo':ejec_p-meta_p, 'meta_anual':meta_a, 'ejec_anual':ejec_a,
        'avance_anual':_pct(ejec_a,meta_a), 'brecha_anual':ejec_a-meta_a,
        'num_months_period':end_num-start_num+1, 'period_label':f'{start_month} – {end_month}'
    }


def generate_pivot_summary_table(df, drill_down_col, start_month, end_month):
    if df.empty: return pd.DataFrame()
    start_num, end_num = MONTH_NUM[start_month], MONTH_NUM[end_month]
    work = df.copy()
    if drill_down_col != 'Sin desagregar' and drill_down_col in work.columns:
        work['Detalle'] = work[drill_down_col].fillna('Sin especificar')
    else:
        work['Detalle'] = 'Total consolidado'
    grouped = work.groupby(['Detalle','Mes'], as_index=False)[['Meta','Ejecutado']].sum()
    pm = grouped.pivot(index='Detalle', columns='Mes', values='Meta').fillna(0)
    pe = grouped.pivot(index='Detalle', columns='Mes', values='Ejecutado').fillna(0)
    pm = pm.reindex(columns=MONTHS_SPANISH, fill_value=0)
    pe = pe.reindex(columns=MONTHS_SPANISH, fill_value=0)
    period = [m for m in MONTHS_SPANISH if start_num <= MONTH_NUM[m] <= end_num]
    rows=[]
    for detail in sorted(set(pm.index) | set(pe.index)):
        row={'Detalle':detail}
        for m in MONTHS_SPANISH:
            row[f'{m}_Meta']=float(pm.loc[detail,m]) if detail in pm.index else 0
            row[f'{m}_Ejec']=float(pe.loc[detail,m]) if detail in pe.index else 0
        mp=sum(row[f'{m}_Meta'] for m in period); ep=sum(row[f'{m}_Ejec'] for m in period)
        ma=sum(row[f'{m}_Meta'] for m in MONTHS_SPANISH); ea=sum(row[f'{m}_Ejec'] for m in MONTHS_SPANISH)
        row.update(Meta_Periodo=mp,Ejec_Periodo=ep,Avance_Periodo=_pct(ep,mp),Meta_Anual=ma,Ejec_Anual=ea,Avance_Anual=_pct(ea,ma))
        rows.append(row)
    res=pd.DataFrame(rows)
    total={'Detalle':'TOTAL'}
    numeric=[c for c in res.columns if c!='Detalle' and not c.startswith('Avance_')]
    for c in numeric: total[c]=res[c].sum()
    total['Avance_Periodo']=_pct(total['Ejec_Periodo'],total['Meta_Periodo'])
    total['Avance_Anual']=_pct(total['Ejec_Anual'],total['Meta_Anual'])
    return pd.concat([res,pd.DataFrame([total])],ignore_index=True)
