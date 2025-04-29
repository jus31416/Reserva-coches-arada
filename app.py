import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_calendar import calendar
import json

# --- CONFIGURACIÓN GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "reservas_arada"

@st.cache_resource
def autenticar_gspread():
    creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, SCOPE)
    cliente = gspread.authorize(creds)
    return cliente

cliente = autenticar_gspread()
hoja = cliente.open(SHEET_NAME)
sheet_reservas = hoja.worksheet("Sheet1")
sheet_mantenimiento = hoja.worksheet("Sheet2")

# (aquí seguiría el resto del código)