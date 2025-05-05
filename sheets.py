import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de acceso
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
client = gspread.authorize(creds)

# Acceso al documento y hojas
spreadsheet = client.open("reservas_arada")
hoja_reservas = spreadsheet.worksheet("Sheet1")
hoja_mantenimiento = spreadsheet.worksheet("Sheet2")

# Lectura de datos
def obtener_reservas():
    df = get_as_dataframe(hoja_reservas, evaluate_formulas=True).dropna(how="all")
    df = df.dropna(subset=["id"]) if "id" in df.columns else df
    return df

def obtener_mantenimientos():
    df = get_as_dataframe(hoja_mantenimiento, evaluate_formulas=True).dropna(how="all")
    df = df.dropna(subset=["id"]) if "id" in df.columns else df
    return df

# Inserción
def insertar_reserva(empleado, vehiculo, inicio, fin, motivo):
    df = obtener_reservas()
    nuevo_id = int(df["id"].max()) + 1 if not df.empty else 1
    nueva = pd.DataFrame([{
        "id": nuevo_id,
        "empleado": empleado,
        "vehiculo": vehiculo,
        "inicio": inicio,
        "fin": fin,
        "motivo": motivo
    }])
    df = pd.concat([df, nueva], ignore_index=True)
    set_with_dataframe(hoja_reservas, df)

def insertar_mantenimiento(vehiculo, inicio, fin, motivo):
    df = obtener_mantenimientos()
    nuevo_id = int(df["id"].max()) + 1 if not df.empty else 1
    nuevo = pd.DataFrame([{
        "id": nuevo_id,
        "vehiculo": vehiculo,
        "inicio": inicio,
        "fin": fin,
        "motivo": motivo
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    set_with_dataframe(hoja_mantenimiento, df)

# Eliminación
def eliminar_reserva(reserva_id):
    df = obtener_reservas()
    df = df[df["id"] != int(reserva_id)]
    set_with_dataframe(hoja_reservas, df)

def eliminar_mantenimiento(mant_id):
    df = obtener_mantenimientos()
    df = df[df["id"] != int(mant_id)]
    set_with_dataframe(hoja_mantenimiento, df)
