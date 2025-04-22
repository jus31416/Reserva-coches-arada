
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

def insertar_reserva(empleado, vehiculo, inicio, fin, motivo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reservas (empleado, vehiculo, inicio, fin, motivo) VALUES (?, ?, ?, ?, ?)",
              (empleado, vehiculo, inicio, fin, motivo))
    conn.commit()
    conn.close()

def insertar_mantenimiento(vehiculo, inicio, fin, motivo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO mantenimiento (vehiculo, inicio, fin, motivo) VALUES (?, ?, ?, ?)",
              (vehiculo, inicio, fin, motivo))
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

def eliminar_reserva(reserva_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
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
    motivo = st.text_input("Motivo (opcional)")
    if st.form_submit_button("Reservar"):
        if empleado == "Seleccionar" or vehiculo == "Seleccionar" or not inicio_hora or not fin_hora:
            st.error("Debes completar todos los campos.")
        else:
            inicio = datetime.combine(inicio_fecha, inicio_hora)
            fin = datetime.combine(fin_fecha, fin_hora)
            if inicio >= fin:
                st.error("La fecha/hora de inicio debe ser anterior a la de fin.")
            else:
                reservas_df = obtener_reservas()
                solape = reservas_df[(reservas_df["vehiculo"] == vehiculo) &
                                     (reservas_df["inicio"] < fin) & (reservas_df["fin"] > inicio)]
                bloqueado = obtener_mantenimientos()[(obtener_mantenimientos()["vehiculo"] == vehiculo) &
                                     (obtener_mantenimientos()["inicio"] < fin) & (obtener_mantenimientos()["fin"] > inicio)]
                if not solape.empty:
                    st.error("❌ Conflicto con otra reserva.")
                elif not bloqueado.empty:
                    st.error("🔧 Vehículo bloqueado por mantenimiento.")
                else:
                    insertar_reserva(empleado, vehiculo, inicio.isoformat(), fin.isoformat(), motivo)
                    st.success("✅ Reserva registrada.")

st.header("🔧 Bloquear vehículo por mantenimiento")
with st.form("form_mantenimiento"):
    vehiculo_m = st.selectbox("Vehículo", vehiculos[1:], key="vehiculo_m")
    inicio_fecha_m = st.date_input("Fecha inicio", key="fecha_inicio_m")
    inicio_hora_m = st.time_input("Hora inicio", key="hora_inicio_m", value=None)
    fin_fecha_m = st.date_input("Fecha fin", key="fecha_fin_m")
    fin_hora_m = st.time_input("Hora fin", key="hora_fin_m", value=None)
    motivo_m = st.text_input("Motivo", key="motivo_m")
    if st.form_submit_button("Añadir bloqueo"):
        if not inicio_hora_m or not fin_hora_m:
            st.error("Debes indicar fecha y hora completas.")
        else:
            inicio_m = datetime.combine(inicio_fecha_m, inicio_hora_m)
            fin_m = datetime.combine(fin_fecha_m, fin_hora_m)
            if inicio_m >= fin_m:
                st.error("La fecha/hora de inicio debe ser anterior a la de fin.")
            else:
                insertar_mantenimiento(vehiculo_m, inicio_m.isoformat(), fin_m.isoformat(), motivo_m)
                st.success("🛠 Bloqueo añadido.")

st.header("📊 Calendario")
reservas = obtener_reservas()
mantenimiento = obtener_mantenimientos()
eventos = []

for _, row in reservas.iterrows():
    eventos.append({
        "title": f"{row['vehiculo']} - {row['empleado']}",
        "start": row["inicio"].isoformat(),
        "end": row["fin"].isoformat(),
        "color": colores_vehiculo.get(row["vehiculo"], "#1f77b4")
    })

for _, row in mantenimiento.iterrows():
    eventos.append({
        "title": f"Mantenimiento - {row['vehiculo']}",
        "start": row["inicio"].isoformat(),
        "end": row["fin"].isoformat(),
        "color": "#808080"
    })

calendar(events=eventos, options={
    "initialView": "timeGridWeek",
    "locale": "es",
    "slotMinTime": "07:00:00",
    "slotMaxTime": "21:00:00",
    "height": 600
})

st.header("❌ Anular reserva")
if not reservas.empty:
    reservas["texto"] = reservas.apply(lambda r: f"{r['empleado']} - {r['vehiculo']} ({r['inicio']} a {r['fin']})", axis=1)
    seleccion = st.selectbox("Selecciona una reserva", ["Seleccionar"] + reservas["texto"].tolist())
    if seleccion != "Seleccionar":
        id_reserva = reservas[reservas["texto"] == seleccion]["id"].values[0]
        if st.button("Anular reserva"):
            eliminar_reserva(id_reserva)
            st.success("✅ Reserva anulada.")
else:
    st.info("No hay reservas disponibles.")

with st.expander("📦 Exportar datos"):
    col1, col2 = st.columns(2)
    col1.download_button("Exportar reservas", reservas.to_csv(index=False).encode("utf-8"), "reservas.csv")
    col2.download_button("Exportar mantenimiento", mantenimiento.to_csv(index=False).encode("utf-8"), "mantenimiento.csv")
