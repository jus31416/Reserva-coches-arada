import pandas as pd
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2 import service_account

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = st.secrets["SHEET_ID"]

def auth_gsheets():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPE)
    client = gspread.authorize(credentials)
    return client.open_by_key(SHEET_ID)

def cargar_datos():
    ss = auth_gsheets()
    sheet1 = ss.worksheet("Sheet1").get_all_records()
    sheet2 = ss.worksheet("Sheet2").get_all_records()
    df1 = pd.DataFrame(sheet1)
    df2 = pd.DataFrame(sheet2)
    for df in [df1, df2]:
        if not df.empty:
            for col in ["Inicio", "Fin"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
    return df1, df2

def guardar_reserva(empleado, vehiculo, inicio, fin, motivo):
    ss = auth_gsheets()
    ss.worksheet("Sheet1").append_row([empleado, vehiculo, str(inicio), str(fin), motivo])

def guardar_mantenimiento(vehiculo, inicio, fin, motivo):
    ss = auth_gsheets()
    ss.worksheet("Sheet2").append_row([vehiculo, str(inicio), str(fin), motivo])

def borrar_reserva(index):
    ss = auth_gsheets()
    ss.worksheet("Sheet1").delete_rows(index + 2)
