import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ID ÚNICO DE TU PLANILLA (Extraído de tu URL)
SPREADSHEET_ID = "1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0"
URL_FINAL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Limpieza visual
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Intentamos leer Socios. Si falla acá, es el nombre de la pestaña.
        df_s = conn.read(spreadsheet=URL_FINAL, worksheet="Socios", ttl=0)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        
        # Intentamos leer Reservas
        try:
            df_r = conn.read(spreadsheet=URL_FINAL, worksheet="Reservas", ttl=0)
            df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        except:
            # Si no existe Reservas, creamos un DataFrame vacío para que no explote
            df_r = pd.DataFrame(columns=['socio_id', 'fecha', 'hora'])
            
        return df_s, df_r
    except Exception as e:
        # Esto nos va a decir exactamente qué está fallando
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- INTERFAZ ---
st.title("🏋️ Arca S&S")
menu = st.radio("Sección:", ["Alumnos", "Administración 🔒"], horizontal=True)

df_s, df_r = cargar_datos()

if menu == "Alumnos":
    if not df_s.empty:
        df_s['full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Seleccioná tu nombre:", [""] + df_s['full'].tolist())
        
        if alumno:
            idx = df_s[df_s['full'] == alumno].index[0]
            saldo = int(df_s.at[idx, 'saldo_clases'])
            st.info(f"Hola **{alumno}**. Clases restantes: **{saldo}**")
            
            if saldo > 0:
                fec = st.date_input("Fecha")
                hor = st.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR TURNO"):
                    nueva = pd.DataFrame([{"socio_id": str(alumno), "fecha": str(fec), "hora": str(hor)}])
                    df_r_act = pd.concat([df_r, nueva], ignore_index=True)
                    conn.update(spreadsheet=URL_FINAL, worksheet="Reservas", data=df_r_act)
                    
                    df_s.at[idx, 'saldo_clases'] = saldo - 1
                    df_subir = df_s.drop(columns=['full'])
                    conn.update(spreadsheet=URL_FINAL, worksheet="Socios", data=df_subir)
                    st.balloons()
                    st.rerun()

else:
    clave = st.text_input("Clave:", type="password")
    if clave == "Samuel28":
        t1, t2, t3 = st.tabs(["📅 Agenda", "👥 Socios", "➕ Gestión"])
        with t2:
            if not df_s.empty:
                st.dataframe(df_s[['nombre', 'apellido', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)
        with t3:
            with st.form("alta"):
                n = st.text_input("Nombre"); a = st.text_input("Apellido")
                s = st.number_input("Clases", value=8); v = st.date_input("Vencimiento")
                if st.form_submit_button("GUARDAR EN DRIVE"):
                    nuevo = pd.DataFrame([{"nombre": str(n), "apellido": str(a), "contacto": "-", "saldo_clases": int(s), "vencimiento": str(v)}])
                    df_final = pd.concat([df_s.drop(columns=['full'] if 'full' in df_s.columns else []), nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_FINAL, worksheet="Socios", data=df_final)
                    st.success("¡Guardado!")
                    st.rerun()
