import os
import re
from pathlib import Path
import pandas as pd
import streamlit as st


def get_data_dir():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_available_years():
    data_dir = get_data_dir()
    meta_years, ejec_years = set(), set()
    pattern = re.compile(r'^(meta|ejecucion)_(\d{4})\.xlsx$', re.IGNORECASE)
    for file in data_dir.iterdir():
        if not file.is_file():
            continue
        match = pattern.match(file.name)
        if match:
            kind, year = match.groups()
            (meta_years if kind.lower() == 'meta' else ejec_years).add(int(year))
    return sorted(meta_years & ejec_years)


def get_file_modification_time(year):
    path = get_data_dir() / f"ejecucion_{year}.xlsx"
    if not path.exists():
        return "No disponible"
    return pd.to_datetime(os.path.getmtime(path), unit='s').strftime('%d/%m/%Y %H:%M:%S')


@st.cache_data(show_spinner=False)
def load_year_data(year):
    data_dir = get_data_dir()
    meta_path = data_dir / f"meta_{year}.xlsx"
    ejec_path = data_dir / f"ejecucion_{year}.xlsx"
    if not meta_path.exists():
        raise FileNotFoundError(f"No se encontró data/{meta_path.name}")
    if not ejec_path.exists():
        raise FileNotFoundError(f"No se encontró data/{ejec_path.name}")

    meta_excel = pd.ExcelFile(meta_path)
    ejec_excel = pd.ExcelFile(ejec_path)

    def find_sheet(excel_file, keyword):
        for sheet in excel_file.sheet_names:
            if keyword.upper() in sheet.strip().upper():
                return sheet
        return None

    sm = find_sheet(meta_excel, "SERVICIOS")
    se = find_sheet(ejec_excel, "SERVICIOS")
    um = find_sheet(meta_excel, "UP")
    ue = find_sheet(ejec_excel, "UP")
    missing = []
    if not sm: missing.append(f"hoja de SERVICIOS en {meta_path.name}")
    if not se: missing.append(f"hoja de SERVICIOS en {ejec_path.name}")
    if not um: missing.append(f"hoja de UP en {meta_path.name}")
    if not ue: missing.append(f"hoja de UP en {ejec_path.name}")
    if missing:
        raise ValueError("No se encontró: " + ", ".join(missing))

    return {
        "meta_servicios": pd.read_excel(meta_excel, sheet_name=sm),
        "ejecucion_servicios": pd.read_excel(ejec_excel, sheet_name=se),
        "meta_up": pd.read_excel(meta_excel, sheet_name=um),
        "ejecucion_up": pd.read_excel(ejec_excel, sheet_name=ue),
    }
