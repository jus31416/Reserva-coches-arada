import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from google_sheets_helper import cargar_datos, guardar_reserva, guardar_mantenimiento, borrar_reserva
from streamlit_calendar import calendar

st.set_page_config(page_title="Gestor de reservas de coches arada", layout="wide")
st.title("🚗 Gestor de reservas de coches arada")

st.markdown("### 📅 Nueva reserva")
empleados = ["Seleccionar"] + sorted([
    "Antonio José", "Antonio Miguel", "Berta", "Encar", "Felipe", "Jose David", "Juanjo", "Juanma Fdez.",
    "Juanma Pelegrín", "Justa", "Mari Huertas", "Mayca", "Miguel Ángel", "Pedro", "Raúl"
])
vehiculos = ["Seleccionar", "Micra", "Sandero", "Duster"]
colores_vehiculo = {"Micra": "#1f77b4", "Sandero": "#2ca02c", "Duster": "#ff7f0e"}

reservas_df, mantenimiento_df = cargar_datos()

with st.form("reserva_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        empleado = st.selectbox("Empleado", empleados)
        vehiculo = st.selectbox("Vehículo", vehiculos)
    with col2:
        fecha_inicio = st.date_input("Fecha inicio")
        hora_inicio = st.time_input("Hora inicio")
    with col3:
        fecha_fin = st.date_input("Fecha fin")
        hora_fin = st.time_input("Hora fin")
    motivo = st.text_input("Motivo")
    if st.form_submit_button("Reservar"):
        if empleado == "Seleccionar" or vehiculo == "Seleccionar" or not motivo:
            st.warning("Por favor completa todos los campos obligatorios.")
        else:
            inicio = datetime.combine(fecha_inicio, hora_inicio)
            fin = datetime.combine(fecha_fin, hora_fin)
            conflicto_r = reservas_df[(reservas_df["Vehículo"] == vehiculo) & (reservas_df["Inicio"] < fin) & (reservas_df["Fin"] > inicio)]
            conflicto_m = mantenimiento_df[(mantenimiento_df["Vehículo"] == vehiculo) & (mantenimiento_df["Inicio"] < fin) & (mantenimiento_df["Fin"] > inicio)]
            if not conflicto_r.empty:
                st.error("❌ Conflicto con otra reserva.")
            elif not conflicto_m.empty:
                st.error("⚠️ Conflicto con mantenimiento.")
            else:
                guardar_reserva(empleado, vehiculo, inicio, fin, motivo)
                st.success("✅ Reserva añadida correctamente.")
                st.experimental_rerun()

st.markdown("### 🔧 Bloquear vehículo por mantenimiento")
with st.form("mantenimiento_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        vehiculo_m = st.selectbox("Vehículo", vehiculos[1:], key="veh_m")
    with col2:
        fecha_inicio_m = st.date_input("Fecha inicio", key="fecha_inicio_m")
        hora_inicio_m = st.time_input("Hora inicio", key="hora_inicio_m")
    with col3:
        fecha_fin_m = st.date_input("Fecha fin", key="fecha_fin_m")
        hora_fin_m = st.time_input("Hora fin", key="hora_fin_m")
    motivo_m = st.text_input("Motivo", key="motivo_m")
    if st.form_submit_button("Añadir mantenimiento"):
        inicio_m = datetime.combine(fecha_inicio_m, hora_inicio_m)
        fin_m = datetime.combine(fecha_fin_m, hora_fin_m)
        guardar_mantenimiento(vehiculo_m, inicio_m, fin_m, motivo_m)
        st.success("✅ Mantenimiento añadido correctamente.")
        st.experimental_rerun()

st.markdown("### 📆 Calendario de reservas y mantenimientos")
eventos = []
for _, row in reservas_df.iterrows():
    eventos.append({
        "title": f"{row['Vehículo']} - {row['Empleado']} ({row['Motivo']})",
        "start": row["Inicio"],
        "end": row["Fin"],
        "color": colores_vehiculo.get(row["Vehículo"], "#1f77b4")
    })
for _, row in mantenimiento_df.iterrows():
    eventos.append({
        "title": f"Mantenimiento - {row['Vehículo']} ({row['Motivo']})",
        "start": row["Inicio"],
        "end": row["Fin"],
        "color": "#808080"
    })

calendar(events=eventos, options={"locale": "es", "initialView": "timeGridWeek", "firstDay": 1})

st.markdown("### ❌ Anular reserva")
if not reservas_df.empty:
    reservas_df["Resumen"] = reservas_df.apply(lambda x: f"{x['Empleado']} - {x['Vehículo']} ({x['Inicio']} - {x['Fin']})", axis=1)
    seleccion = st.selectbox("Selecciona una reserva", ["Seleccionar"] + reservas_df["Resumen"].tolist())
    if seleccion != "Seleccionar":
        if st.button("Eliminar"):
            idx = reservas_df[reservas_df["Resumen"] == seleccion].index[0]
            borrar_reserva(idx)
            st.success("✅ Reserva eliminada.")
            st.experimental_rerun()

with st.expander("📦 Exportar datos"):
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📄 Exportar reservas", reservas_df.to_csv(index=False), file_name="reservas.csv")
    with col2:
        st.download_button("📄 Exportar mantenimiento", mantenimiento_df.to_csv(index=False), file_name="mantenimiento.csv")
