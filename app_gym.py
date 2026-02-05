import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DIRECTA DE TU PLANILLA
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar basura visual
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Cargamos los datos sin usar los Secrets para evitar el Error 400
        df_s = conn.read(spreadsheet=URL_PLANILLA, worksheet="Socios", ttl=0)
        df_r = conn.read(spreadsheet=URL_PLANILLA, worksheet="Reservas", ttl=0)
        
        # Limpiar columnas
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Vista Alumnos", "Administración 🔒"])

# --- VISTA ALUMNOS ---
if modo == "Vista Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    df_s, df_r = cargar_datos()
    
    if not df_s.empty:
        # Combinamos nombre y apellido
        df_s['nombre_full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Seleccioná tu nombre", [""] + df_s['nombre_full'].tolist())
        
        if alumno:
            idx = df_s[df_s['nombre_full'] == alumno].index[0]
            saldo = df_s.at[idx, 'saldo_clases']
            st.info(f"Hola **{alumno}**. Tenés **{int(saldo)}** clases restantes.")
            
            if saldo > 0:
                fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
                hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR RESERVA", use_container_width=True):
                    # 1. Guardar Reserva
                    nueva_r = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                    df_r_act = pd.concat([df_r, nueva_r], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, worksheet="Reservas", data=df_r_act)
                    
                    # 2. Descontar Saldo
                    df_s.at[idx, 'saldo_clases'] = saldo - 1
                    conn.update(spreadsheet=URL_PLANILLA, worksheet="Socios", data=df_s.drop(columns=['nombre_full']))
                    
                    st.balloons()
                    st.success("¡Tu horario está confirmado! Si no podés venir, ¡avisanos!")
                    st.rerun()
    else:
        st.warning("Verificá la conexión en el Drive.")

# --- VISTA ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Gestión")
    clave = st.sidebar.text_input("Clave Admin", type="password")
    
    if clave == "Samuel28":
        df_s, df_r = cargar_datos()
        tab1, tab2, tab3 = st.tabs(["📅 Agenda", "👥 Socios", "🛠️ Gestión"])

        with tab1:
            dia = st.date_input("Ver turnos de:", value=pd.to_datetime("today"))
            if not df_r.empty:
                hoy = df_r[df_r['fecha'] == str(dia)]
                st.dataframe(hoy[['socio_id', 'hora']], use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("Acciones de Administrador")
            with st.form("admin_arca"):
                n = st.text_input("Nombre")
                a = st.text_input("Apellido")
                s = st.number_input("Clases", value=8)
                if st.form_submit_button("Dar de Alta / Cargar Pack"):
                    nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "saldo_clases": s, "contacto": "-", "vencimiento": "2026-12-31"}])
                    df_final_s = pd.concat([df_s, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, worksheet="Socios", data=df_final_s)
                    st.success("¡Operación exitosa!")
                    st.rerun()
    else:
        st.info("Ingresá la clave 'Samuel28' para administrar.")
