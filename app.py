
import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Depuración conexión Google Sheets", layout="wide")
st.title("🔍 Diagnóstico conexión con Google Sheets")

# Paso 1: leer credenciales y conectarse
st.subheader("1. Autenticación con Google Sheets")
try:
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    SHEET_NAME = "reservas_arada"
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    st.success("✅ Conexión con Google autorizada.")
except Exception as e:
    st.error("❌ Error durante la autenticación:")
    st.exception(e)
    st.stop()

# Paso 2: abrir el documento
st.subheader("2. Acceso al documento")
try:
    doc = client.open(SHEET_NAME)
    st.success(f"✅ Documento '{SHEET_NAME}' abierto correctamente.")
    sheet_list = [sh.title for sh in doc.worksheets()]
    st.write("Hojas encontradas:", sheet_list)
except Exception as e:
    st.error("❌ No se pudo abrir el documento o listar las hojas.")
    st.exception(e)
    st.stop()

# Paso 3: leer Sheet1 y Sheet2
st.subheader("3. Lectura de hojas")
try:
    ws1 = doc.worksheet("Sheet1")
    df1 = pd.DataFrame(ws1.get_all_records())
    st.write("📄 Contenido de Sheet1 (Reservas):")
    st.dataframe(df1)
except Exception as e:
    st.error("❌ Error al leer Sheet1")
    st.exception(e)

try:
    ws2 = doc.worksheet("Sheet2")
    df2 = pd.DataFrame(ws2.get_all_records())
    st.write("📄 Contenido de Sheet2 (Mantenimiento):")
    st.dataframe(df2)
except Exception as e:
    st.error("❌ Error al leer Sheet2")
    st.exception(e)

st.info("👆 Si ves errores arriba, revisa que ambas hojas existan y tengan columnas.")
