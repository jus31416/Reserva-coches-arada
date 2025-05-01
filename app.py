
import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_calendar import calendar
import json

# Mensaje de carga inicial
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

# Manejo de errores al conectar con Google Sheets
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

# --- CONFIGURACIÓN APP ---
st.set_page_config(page_title="Gestor de reservas de coches arada", layout="wide")
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

# --- NUEVA RESERVA ---
st.header("📅 Nueva reserva")
with st.form("form_reserva"):
    empleado = st.selectbox("Empleado", empleados, index=0)
    vehiculo = st.selectbox("Vehículo", vehiculos, index=0)
    inicio_fecha = st.date_input("Fecha de inicio")
    inicio_hora = st.time_input("Hora de inicio", value=None)
    fin_fecha = st.date_input("Fecha de fin")
    fin_hora = st.time_input("Hora de fin", value=None)
    motivo = st.text_input("Motivo")
    if st.form_submit_button("Reservar"):
        if empleado == "Seleccionar" or vehiculo == "Seleccionar" or not inicio_hora or not fin_hora or not motivo.strip():
            st.error("Debes completar todos los campos.")
        else:
            inicio = datetime.combine(inicio_fecha, inicio_hora)
            fin = datetime.combine(fin_fecha, fin_hora)
            if inicio >= fin:
                st.error("La fecha/hora de inicio debe ser anterior a la de fin.")
            else:
                conflicto = reservas_df[(reservas_df["Vehículo"] == vehiculo) & ((reservas_df["Inicio"] < fin) & (reservas_df["Fin"] > inicio))]
                mantenimiento_conf = mantenimiento_df[(mantenimiento_df["Vehículo"] == vehiculo) & ((mantenimiento_df["Inicio"] < fin) & (mantenimiento_df["Fin"] > inicio))]
                if not conflicto.empty:
                    st.error("❌ Ya hay una reserva en ese intervalo.")
                elif not mantenimiento_conf.empty:
                    st.error("🔧 El vehículo está bloqueado por mantenimiento.")
                else:
                    nueva = pd.DataFrame([{
                        "Empleado": empleado,
                        "Vehículo": vehiculo,
                        "Inicio": inicio,
                        "Fin": fin,
                        "Motivo": motivo
                    }])
                    reservas_df = pd.concat([reservas_df, nueva], ignore_index=True)
                    guardar_reservas(reservas_df)
                    st.success("✅ Reserva realizada correctamente.")
                    st.rerun()

# --- MANTENIMIENTO ---
st.header("🔧 Bloquear vehículo por mantenimiento")
with st.form("form_mantenimiento"):
    vehiculo_m = st.selectbox("Vehículo", vehiculos[1:], key="vehiculo_m")
    inicio_fecha_m = st.date_input("Fecha inicio", key="fecha_inicio_m")
    inicio_hora_m = st.time_input("Hora inicio", key="hora_inicio_m", value=None)
    fin_fecha_m = st.date_input("Fecha fin", key="fecha_fin_m")
    fin_hora_m = st.time_input("Hora fin", key="hora_fin_m", value=None)
    motivo_m = st.text_input("Motivo", key="motivo_m")
    if st.form_submit_button("Añadir bloqueo"):
        if not inicio_hora_m or not fin_hora_m or not motivo_m.strip():
            st.error("Debes completar todos los campos.")
        else:
            inicio_m = datetime.combine(inicio_fecha_m, inicio_hora_m)
            fin_m = datetime.combine(fin_fecha_m, fin_hora_m)
            if inicio_m >= fin_m:
                st.error("La fecha/hora de inicio debe ser anterior a la de fin.")
            else:
                nueva_m = pd.DataFrame([{
                    "Vehículo": vehiculo_m,
                    "Inicio": inicio_m,
                    "Fin": fin_m,
                    "Motivo": motivo_m
                }])
                mantenimiento_df = pd.concat([mantenimiento_df, nueva_m], ignore_index=True)
                guardar_mantenimientos(mantenimiento_df)
                st.success("🛠️ Mantenimiento registrado.")
                st.rerun()

# --- ANULAR RESERVA ---
st.header("❌ Anular reserva")
if not reservas_df.empty:
    reservas_df["Resumen"] = reservas_df.apply(lambda row: f"{row['Empleado']} - {row['Vehículo']} ({row['Inicio']} - {row['Fin']})", axis=1)
    seleccion = st.selectbox("Selecciona una reserva", ["Seleccionar"] + reservas_df["Resumen"].tolist())
    if seleccion != "Seleccionar":
        if st.button("Anular reserva"):
            reservas_df = reservas_df[reservas_df["Resumen"] != seleccion].drop(columns=["Resumen"])
            guardar_reservas(reservas_df)
            st.success("✅ Reserva anulada.")
            st.rerun()
else:
    st.info("No hay reservas disponibles.")

# --- CALENDARIO ---
st.header("📊 Calendario semanal de reservas")
eventos = []
for _, row in reservas_df.iterrows():
    eventos.append({
        "title": f"{row['Vehículo']} - {row['Empleado']} ({row['Motivo']})",
        "start": row["Inicio"].isoformat(),
        "end": row["Fin"].isoformat(),
        "color": colores_vehiculo.get(row["Vehículo"], "#1f77b4")
    })
for _, row in mantenimiento_df.iterrows():
    eventos.append({
        "title": f"Mantenimiento - {row['Vehículo']} ({row['Motivo']})",
        "start": row["Inicio"].isoformat(),
        "end": row["Fin"].isoformat(),
        "color": "#808080"
    })

calendar(events=eventos, options={
    "initialView": "timeGridWeek",
    "locale": "es",
    "firstDay": 1,
    "slotMinTime": "07:00:00",
    "slotMaxTime": "21:00:00",
    "height": 600
})
