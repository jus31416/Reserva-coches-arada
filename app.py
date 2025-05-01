
import streamlit as st
st.set_page_config(page_title="Gestor de reservas de coches arada", layout="wide")

import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_calendar import calendar
import json

st.write("🔍 Cargando aplicación...")

# --- CONFIGURACIÓN GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "reservas_arada"

@st.cache_resource
def autenticar_gspread():
    creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, SCOPE)
    cliente = gspread.authorize(creds)
    return cliente

try:
    cliente = autenticar_gspread()
    hoja = cliente.open(SHEET_NAME)
    sheet_reservas = hoja.worksheet("Sheet1")
    sheet_mantenimiento = hoja.worksheet("Sheet2")
except Exception as e:
    st.error("❌ Error al conectarse con Google Sheets")
    st.exception(e)
    st.stop()

def cargar_reservas():
    df = get_as_dataframe(sheet_reservas, evaluate_formulas=True).dropna(how="all")
    if not df.empty:
        df["Inicio"] = pd.to_datetime(df["Inicio"])
        df["Fin"] = pd.to_datetime(df["Fin"])
    return df

def cargar_mantenimientos():
    df = get_as_dataframe(sheet_mantenimiento, evaluate_formulas=True).dropna(how="all")
    if not df.empty:
        df["Inicio"] = pd.to_datetime(df["Inicio"])
        df["Fin"] = pd.to_datetime(df["Fin"])
    return df

def guardar_reservas(df):
    sheet_reservas.clear()
    set_with_dataframe(sheet_reservas, df)

def guardar_mantenimientos(df):
    sheet_mantenimiento.clear()
    set_with_dataframe(sheet_mantenimiento, df)

st.title("🚗 Gestor de reservas de coches arada")

empleados = ["Seleccionar"] + sorted([
    "Antonio José", "Antonio Miguel", "Berta", "Encar", "Felipe",
    "Jose David", "Juanjo", "Juanma Fdez.", "Juanma Pelegrín", "Justa",
    "Mari Huertas", "Mayca", "Miguel Ángel", "Pedro", "Raúl"
])
vehiculos = ["Seleccionar", "Micra", "Sandero", "Duster"]
colores_vehiculo = {"Micra": "#1f77b4", "Sandero": "#2ca02c", "Duster": "#ff7f0e"}

reservas_df = cargar_reservas()
mantenimiento_df = cargar_mantenimientos()

# (El resto del código sigue igual al anterior para reserva, mantenimiento, anulación y calendario)
