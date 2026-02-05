import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import os

# --- CONFIGURACIÓN ---
URL_LECTURA_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"
URL_LECTURA_RESERVAS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"
URL_ESCRITURA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"
CELULAR_ADMIN = "549XXXXXXXXXX" # <--- ¡PONÉ TU NÚMERO ACÁ!

st.set_page_config(page_title="Arca S&S", layout="centered")
# Ocultamos el menú hamburguesa de Streamlit para limpiar la vista
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Intentamos conexión
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

def leer_datos():
    try:
        df_s = pd.read_csv(URL_LECTURA_SOCIOS)
        df_r = pd.read_csv(URL_LECTURA_RESERVAS)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except:
        return pd.DataFrame(), pd.DataFrame()

def intentar_guardar(df_socios, df_reservas, mensaje_wpp):
    try:
        if conn:
            conn.update(spreadsheet=URL_ESCRITURA, worksheet="Reservas", data=df_reservas)
            conn.update(spreadsheet=URL_ESCRITURA, worksheet="Socios", data=df_socios)
            st.balloons()
            st.success("✅ ¡Guardado en el sistema!")
            st.rerun()
        else:
            raise Exception("Sin conexión")
    except:
        texto = urllib.parse.quote(mensaje_wpp)
        link = f"https://wa.me/{CELULAR_ADMIN}?text={texto}"
        st.warning("⚠️ No se pudo conectar al Drive automáticamente.")
        st.markdown(f'''
            <a href="{link}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366;color:white;padding:15px;text-align:center;border-radius:10px;font-weight:bold;font-family:sans-serif;">
                    🚀 CONFIRMAR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- MENÚ VISIBLE (SIN BARRA LATERAL) ---
st.title("🏋️ Arca S&S")
# Usamos tabs grandes arriba para que sea fácil cambiar
pestana = st.radio("Menú:", ["Soy Alumno", "Soy Administrador 🔒"], horizontal=True)
st.write("---") # Línea separadora

df_s, df_r = leer_datos()

# --- VISTA ALUMNO ---
if pestana == "Soy Alumno":
    if os.path.exists("logo.png"): st.image("logo.png", width=100)
    
    if not df_s.empty:
        df_s['nombre_full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Buscá tu nombre:", [""] + df_s['nombre_full'].tolist())
        
        if alumno:
            idx = df_s[df_s['nombre_full'] == alumno].index[0]
            saldo = df_s.at[idx, 'saldo_clases']
            
            # Tarjeta de Info
            st.info(f"👋 Hola **{alumno}**\n\n🔋 Clases disponibles: **{int(saldo)}**")
            
            if saldo > 0:
                col1, col2 = st.columns(2)
                with col1:
                    fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
                with col2:
                    hor = st.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("RESERVAR LUGAR", use_container_width=True, type="primary"):
                    nueva_r = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                    df_r_new = pd.concat([df_r, nueva_r], ignore_index=True)
                    
                    df_s.at[idx, 'saldo_clases'] = saldo - 1
                    df_s_new = df_s.drop(columns=['nombre_full'])
                    
                    msg = f"Hola! Soy {alumno}. Voy el {fec} a las {hor}. (Me quedan {saldo-1} clases)"
                    intentar_guardar(df_s_new, df_r_new, msg)

# --- VISTA ADMIN ---
else:
    clave = st.text_input("🔑 Clave de Acceso:", type="password")
    if clave == "Samuel28":
        tab1, tab2, tab3 = st.tabs(["📅 Agenda", "👥 Socios", "➕ Acciones"])
        
        with tab1:
            dia = st.date_input("Ver día:", value=pd.to_datetime("today"))
            if not df_r.empty:
                filtro = df_r[df_r['fecha'] == str(dia)]
                if not filtro.empty:
                    st.dataframe(filtro[['socio_id', 'hora']], use_container_width=True, hide_index=True)
                else:
                    st.write("Nada por aquí.")
        
        with tab2:
            if not df_s.empty:
                st.dataframe(df_s[['nombre', '
