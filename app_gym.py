import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import os

# --- CONFIGURACIÓN ---
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"
CELULAR_SOFIA = "549299XXXXXXX" # <--- Poné el número de Sofía acá

st.set_page_config(page_title="Arca S&S", layout="centered")

# Intentamos la conexión oficial para escribir
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

def cargar_datos():
    try:
        # Leemos con ttl=0 para que siempre traiga lo último del Drive
        df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
        df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except:
        # Si falla, leemos el backup público (Solo lectura)
        url_s = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"
        df_s = pd.read_csv(url_s)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        return df_s, pd.DataFrame()

# --- INTERFAZ ---
st.title("🏋️ Arca S&S")
menu = st.radio("Sección:", ["Alumnos", "Administración 🔒"], horizontal=True)
st.write("---")

df_s, df_r = cargar_datos()

if menu == "Alumnos":
    if not df_s.empty:
        df_s['full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Tu nombre:", [""] + df_s['full'].tolist())
        if alumno:
            # Aquí va el resto de la lógica de reserva que ya tenés...
            st.info(f"Hola **{alumno}**. Seleccioná tu horario.")

else:
    clave = st.text_input("Clave Admin:", type="password")
    if clave == "Samuel28":
        t1, t2, t3 = st.tabs(["📅 Agenda", "👥 Socios", "➕ Alta/Abono"])
        
        with t2:
            st.dataframe(df_s[['nombre', 'apellido', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)
        
        with t3:
            st.subheader("Cargar Nuevo Socio")
            with st.form("alta_directa"):
                n = st.text_input("Nombre")
                a = st.text_input("Apellido")
                s = st.number_input("Clases", value=8)
                v = st.date_input("Vencimiento")
                if st.form_submit_button("GUARDAR EN DRIVE"):
                    try:
                        nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "saldo_clases": s, "vencimiento": str(v), "contacto": "-"}])
                        df_final = pd.concat([df_s, nuevo], ignore_index=True)
                        # ESTA LÍNEA ES LA QUE ESCRIBE EN EL DRIVE
                        conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_final)
                        st.balloons()
                        st.success(f"¡{n} guardado con éxito!")
                        st.rerun()
                    except Exception as e:
                        st.error("No se pudo guardar automático (Faltan permisos en Secrets).")
                        # Opción de respaldo por WhatsApp
                        msg = f"ALTA: {n} {a}, {s} clases, vence {v}"
                        st.markdown(f'[📱 Enviar a Sofía por WhatsApp](https://wa.me/{CELULAR_SOFIA}?text={urllib.parse.quote(msg)})')
