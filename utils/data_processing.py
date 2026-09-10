import re
import unicodedata
import pandas as pd
import numpy as np

MONTHS_SPANISH = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
MONTH_ABBR = {'Enero':'Ene','Febrero':'Feb','Marzo':'Mar','Abril':'Abr','Mayo':'May','Junio':'Jun','Julio':'Jul','Agosto':'Ago','Septiembre':'Set','Octubre':'Oct','Noviembre':'Nov','Diciembre':'Dic'}
MONTH_NUM = {m:i+1 for i,m in enumerate(MONTHS_SPANISH)}
_MONTH_ALIASES = {
    'ENE':'Enero','ENERO':'Enero','FEB':'Febrero','FEBRERO':'Febrero','MAR':'Marzo','MARZO':'Marzo',
    'ABR':'Abril','ABRIL':'Abril','MAY':'Mayo','MAYO':'Mayo','JUN':'Junio','JUNIO':'Junio',
    'JUL':'Julio','JULIO':'Julio','AGO':'Agosto','AGOSTO':'Agosto','SET':'Septiembre','SEP':'Septiembre',
    'SEPT':'Septiembre','SETIEMBRE':'Septiembre','SEPTIEMBRE':'Septiembre','OCT':'Octubre','OCTUBRE':'Octubre',
    'NOV':'Noviembre','NOVIEMBRE':'Noviembre','DIC':'Diciembre','DICIEMBRE':'Diciembre'
}


def _plain(text):
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'\s+', ' ', text.strip()).upper()


def clean_column_names(df):
    df = df.copy()
    mapping = {}
    for col in df.columns:
        key = _plain(col)
        if key in _MONTH_ALIASES: mapping[col] = _MONTH_ALIASES[key]
        elif key in {'CITE/UT','CITE / UT','CITE UT'}: mapping[col] = 'CITE/UT'
        elif 'CATEGORIA' in key and 'PRESUPUEST' in key: mapping[col] = 'Categoría presupuestal'
        elif 'TIPO' in key and 'SERVICIO' in key: mapping[col] = 'Tipo de servicio'
        elif 'TAREA' in key: mapping[col] = 'Nombre de tarea'
        elif 'COMPLEJIDAD' in key: mapping[col] = 'Nivel de complejidad'
        elif key == 'TOTAL': mapping[col] = 'Total'
    return df.rename(columns=mapping)


def normalize_text_columns(df):
    df = df.copy()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('string').str.strip().str.replace(r'\s+', ' ', regex=True)
        df[col] = df[col].replace({'': pd.NA})
    return df


def _prepare_one(raw_df, indicator, value_name):
    df = normalize_text_columns(clean_column_names(raw_df))
    dims = ['CITE/UT','Categoría presupuestal']
    if indicator == 'Servicios':
        dims += ['Tipo de servicio','Nombre de tarea','Nivel de complejidad']
    missing_dims = [c for c in dims if c not in df.columns]
    missing_months = [m for m in MONTHS_SPANISH if m not in df.columns]
    if missing_dims:
        raise ValueError('Faltan columnas obligatorias: ' + ', '.join(missing_dims))
    if missing_months:
        raise ValueError('Faltan meses en el archivo: ' + ', '.join(missing_months))

    for col in dims:
        df[col] = df[col].fillna('Sin especificar')
    for m in MONTHS_SPANISH:
        df[m] = pd.to_numeric(df[m], errors='coerce').fillna(0)

    # Consolidar antes del merge evita multiplicaciones many-to-many si hay filas repetidas.
    df = df.groupby(dims, dropna=False, as_index=False)[MONTHS_SPANISH].sum()
    long = df.melt(id_vars=dims, value_vars=MONTHS_SPANISH, var_name='Mes', value_name=value_name)
    return long, dims


def validate_and_prep_dataset(raw_meta_df, raw_ejec_df, indicator='Servicios'):
    meta_long, dims = _prepare_one(raw_meta_df, indicator, 'Meta')
    ejec_long, _ = _prepare_one(raw_ejec_df, indicator, 'Ejecutado')
    merged = meta_long.merge(ejec_long, on=dims + ['Mes'], how='outer', indicator=True)
    merged['Meta'] = merged['Meta'].fillna(0)
    merged['Ejecutado'] = merged['Ejecutado'].fillna(0)
    merged['Mes_Num'] = merged['Mes'].map(MONTH_NUM).astype(int)
    merged['Estado_cruce'] = merged['_merge'].map({'both':'Meta y ejecución','left_only':'Solo meta','right_only':'Solo ejecución'}).astype(str)
    return merged.drop(columns=['_merge'])


def get_filter_options(df, current_cat=None, current_type=None, current_task=None):
    empty = {'categories': [], 'cites': [], 'service_types':['Todos'], 'tasks':['Todas'], 'complexities':['Todas']}
    if df.empty: return empty
    categories = sorted(df['Categoría presupuestal'].dropna().astype(str).unique().tolist())
    f = df[df['Categoría presupuestal'].eq(current_cat)] if current_cat in categories else df
    cites = sorted(f['CITE/UT'].dropna().astype(str).unique().tolist())
    national = next((x for x in cites if x.strip().casefold() == 'itp red cite públicos'.casefold()), None)
    if national:
        cites.remove(national); cites.insert(0, national)
    out = {'categories':categories,'cites':cites,'service_types':['Todos'],'tasks':['Todas'],'complexities':['Todas']}
    if 'Tipo de servicio' in f.columns:
        out['service_types'] = ['Todos'] + sorted(f['Tipo de servicio'].dropna().astype(str).unique().tolist())
        tf = f if not current_type or current_type == 'Todos' else f[f['Tipo de servicio'].eq(current_type)]
        out['tasks'] = ['Todas'] + sorted(tf['Nombre de tarea'].dropna().astype(str).unique().tolist())
        qf = tf if not current_task or current_task == 'Todas' else tf[tf['Nombre de tarea'].eq(current_task)]
        out['complexities'] = ['Todas'] + sorted(qf['Nivel de complejidad'].dropna().astype(str).unique().tolist())
    return out


def filter_dataset(df, category, cite, service_type='Todos', task='Todas', complexity='Todas'):
    f = df.copy()
    if category: f = f[f['Categoría presupuestal'].eq(category)]
    if cite: f = f[f['CITE/UT'].eq(cite)]
    if 'Tipo de servicio' in f.columns and service_type != 'Todos': f = f[f['Tipo de servicio'].eq(service_type)]
    if 'Nombre de tarea' in f.columns and task != 'Todas': f = f[f['Nombre de tarea'].eq(task)]
    if 'Nivel de complejidad' in f.columns and complexity != 'Todas': f = f[f['Nivel de complejidad'].eq(complexity)]
    return f
