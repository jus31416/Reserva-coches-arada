
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from streamlit_calendar import calendar

DB_PATH = "reservas.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS reservas (id INTEGER PRIMARY KEY, empleado TEXT, vehiculo TEXT, inicio TEXT, fin TEXT, motivo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS mantenimiento (id INTEGER PRIMARY KEY, vehiculo TEXT, inicio TEXT, fin TEXT, motivo TEXT)")
    conn.commit()
    conn.close()

def obtener_reservas():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM reservas", conn, parse_dates=["inicio", "fin"])
    conn.close()
    return df

def obtener_mantenimientos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM mantenimiento", conn, parse_dates=["inicio", "fin"])
    conn.close()
    return df

def insertar_reserva(empleado, vehiculo, inicio, fin, motivo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reservas (empleado, vehiculo, inicio, fin, motivo) VALUES (?, ?, ?, ?, ?)",
              (empleado, vehiculo, inicio, fin, motivo))
    conn.commit()
    conn.close()

def eliminar_reserva(reserva_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reservas WHERE id = ?", (int(reserva_id),))
    conn.commit()
    conn.close()

init_db()
st.set_page_config(page_title="Gestor de reservas de coches arada", layout="wide")
st.title("🚗 Gestor de reservas de coches arada")

empleados = ["Seleccionar"] + sorted([
    "Antonio José", "Antonio Miguel", "Berta", "Encar", "Felipe",
    "Jose David", "Juanjo", "Juanma Fdez.", "Juanma Pelegrín", "Justa",
    "Mari Huertas", "Mayca", "Miguel Ángel", "Pedro", "Raúl"
])
vehiculos = ["Seleccionar", "Micra", "Sandero", "Duster"]
colores_vehiculo = {"Micra": "#1f77b4", "Sandero": "#2ca02c", "Duster": "#ff7f0e"}

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
                insertar_reserva(empleado, vehiculo, inicio.isoformat(), fin.isoformat(), motivo)
                st.success("✅ Reserva registrada.")
                st.rerun()

st.header("❌ Anular reserva")
reservas = obtener_reservas()
if not reservas.empty:
    reservas["texto"] = reservas.apply(lambda r: f"{r['empleado']} - {r['vehiculo']} ({r['inicio']} a {r['fin']})", axis=1)
    seleccion = st.selectbox("Selecciona una reserva", ["Seleccionar"] + reservas["texto"].tolist())
    if seleccion != "Seleccionar":
        id_reserva = int(reservas[reservas["texto"] == seleccion]["id"].values[0])
        if st.button("Anular reserva"):
            eliminar_reserva(id_reserva)
            st.success("✅ Reserva anulada correctamente.")
            st.rerun()
else:
    st.info("No hay reservas disponibles.")

# Cargar datos actualizados tras anulación
reservas = obtener_reservas()
mantenimiento = obtener_mantenimientos()

st.header("📊 Calendario")
eventos = []
for _, row in reservas.iterrows():
    eventos.append({
        "title": f"{row['vehiculo']} - {row['empleado']} ({row['motivo']})",
        "start": row["inicio"].isoformat(),
        "end": row["fin"].isoformat(),
        "color": colores_vehiculo.get(row["vehiculo"], "#1f77b4")
    })
for _, row in mantenimiento.iterrows():
    eventos.append({
        "title": f"Mantenimiento - {row['vehiculo']} ({row['motivo']})",
        "start": row["inicio"].isoformat(),
        "end": row["fin"].isoformat(),
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
