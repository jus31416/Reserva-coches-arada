
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Gestor de reservas de coches arada", layout="wide")
st.title("🚗 Gestor de reservas de coches arada")

# Conexión a la base de datos
conn = sqlite3.connect("reservas.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS reservas (id INTEGER PRIMARY KEY, empleado TEXT, vehiculo TEXT, inicio TEXT, fin TEXT, motivo TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS mantenimiento (id INTEGER PRIMARY KEY, vehiculo TEXT, inicio TEXT, fin TEXT, motivo TEXT)")
conn.commit()

st.markdown("Aplicación funcionando con SQLite.")
