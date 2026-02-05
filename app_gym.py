import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- CONFIGURACIÓN ARCA S&S ---
CLAVE_ADMIN = "arca2026"
PACKS = {
    "Pack 8 clases ($45.000)": 8,
    "Pack 12 clases ($50.000)": 12,
    "Pack 16 clases ($55.000)": 16,
    "Pack 20 clases ($58.000)": 20
}
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"]
CUPO_MAX = 8
URL_SHEET = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit#gid=1298454736"

st.set_page_config(page_title="Arca S&S", layout="wide")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_hoja(nombre_hoja):
    return conn.read(spreadsheet=URL_SHEET, worksheet=nombre_hoja, ttl="0s")

# --- INTERFAZ ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.title("Menú Arca S&S")
es_admin = st.sidebar.checkbox("Acceso Administrador")
pwd = st.sidebar.text_input("Contraseña", type="password") if es_admin else ""

if es_admin and pwd == CLAVE_ADMIN:
    menu = ["Reservar Turno", "Mis Reservas / Cancelar", "Registrar Socio / Pago", "Panel de Control (Admin)"]
else:
    menu = ["Reservar Turno", "Mis Reservas / Cancelar"]

choice = st.sidebar.selectbox("Seleccionar:", menu)
hoy = datetime.now()

# --- 1. REGISTRAR SOCIO (ADMIN) ---
if choice == "Registrar Socio / Pago":
    st.title("💳 Registro de Socios y Pagos")
    df_socios = leer_hoja("Socios")
    
    with st.form("form_pago"):
        nombre = st.text_input("Nombre Completo")
        pack = st.selectbox("Pack", list(PACKS.keys()))
        enviar = st.form_submit_button("Confirmar Pago y Cargar Clases")
        
        if enviar and nombre:
            clases = PACKS[pack]
            venc = hoy.replace(day=calendar.monthrange(hoy.year, hoy.month)[1]).strftime("%Y-%m-%d")
            
            # Crear nueva fila
            nueva_fila = pd.DataFrame([{"id": len(df_socios)+1, "nombre": nombre, "pack": pack, "saldo_clases": clases, "vencimiento": venc}])
            df_final = pd.concat([df_socios, nueva_fila], ignore_index=True)
            
            conn.update(spreadsheet=URL_SHEET, worksheet="Socios", data=df_final)
            st.success(f"✅ {nombre} registrado con {clases} clases.")

# --- 2. RESERVAR TURNO (ALUMNO) ---
elif choice == "Reservar Turno":
    st.title("📅 Reserva de Clases")
    df_socios = leer_hoja("Socios")
    df_res = leer_hoja("Reservas")
    
    if not df_socios.empty:
        nom = st.selectbox("Tu Nombre", df_socios['nombre'].tolist())
        s_idx = df_socios.index[df_socios['nombre'] == nom][0]
        s_data = df_socios.iloc[s_idx]
        
        venc_dt = datetime.strptime(str(s_data['vencimiento']), "%Y-%m-%d")
        
        if hoy > venc_dt:
            st.error("🚫 Abono vencido.")
        elif int(s_data['saldo_clases']) <= 0:
            st.error("🚫 Sin clases disponibles.")
        else:
            fec = st.date_input("Fecha", min_value=hoy.date())
            hor = st.selectbox("Hora", HORARIOS)
            
            if st.button("Confirmar Reserva"):
                # Actualizar Reservas
                nueva_res = pd.DataFrame([{"id": len(df_res)+1, "socio_id": s_data['id'], "fecha": str(fec), "hora": hor}])
                df_res_final = pd.concat([df_res, nueva_res], ignore_index=True)
                conn.update(spreadsheet=URL_SHEET, worksheet="Reservas", data=df_res_final)
                
                # Descontar clase
                df_socios.at[s_idx, 'saldo_clases'] = int(s_data['saldo_clases']) - 1
                conn.update(spreadsheet=URL_SHEET, worksheet="Socios", data=df_socios)
                
                st.success(f"✅ Turno confirmado para el {fec}. Te quedan {int(s_data['saldo_clases']) - 1} clases.")

# --- 3. PANEL CONTROL (ADMIN) ---
elif choice == "Panel de Control (Admin)":
    st.title("📊 Control Arca S&S")
    st.write("### Socios")
    st.dataframe(leer_hoja("Socios"))
    st.write("### Reservas Actuales")
    st.dataframe(leer_hoja("Reservas"))