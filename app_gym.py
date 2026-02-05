import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA - Verificada
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# Ocultar menús
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Inicializar conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Forzamos ttl=0 para que siempre traiga datos frescos del Drive
        df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
        df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
        
        # Limpieza de columnas
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Reservas Alumnos", "Administración 🔒"])

# --- VISTA ALUMNOS ---
if modo == "Reservas Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    df_s, df_r = cargar_datos()
    
    if not df_s.empty:
        df_s['nombre_full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Seleccioná tu nombre", [""] + df_s['nombre_full'].tolist())
        
        if alumno:
            idx = df_s[df_s['nombre_full'] == alumno].index[0]
            saldo = df_s.at[idx, 'saldo_clases']
            st.info(f"Hola **{alumno}**. Clases restantes: {int(saldo)}")
            
            if saldo > 0:
                fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
                hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR TURNO", use_container_width=True):
                    # Guardar Reserva
                    nueva_r = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                    df_r_act = pd.concat([df_r, nueva_r], ignore_index=True)
                    conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_r_act)
                    
                    # Descontar Saldo
                    df_s.at[idx, 'saldo_clases'] = saldo - 1
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s.drop(columns=['nombre_full']))
                    
                    st.balloons()
                    st.success("¡Confirmado! Si no podés venir, avisale a Sofía.")
                    st.rerun()
    else:
        st.warning("Conectando con la base de datos...")

# --- VISTA ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Gestión")
    clave = st.sidebar.text_input("Clave de Acceso", type="password")
    
    if clave == "Samuel28":
        df_s, df_r = cargar_datos()
        tab1, tab2, tab3 = st.tabs(["📅 Agenda", "👥 Socios", "🛠️ Acciones"])

        with tab1:
            dia = st.date_input("Día:", value=pd.to_datetime("today"))
            hoy = df_r[df_r['fecha'] == str(dia)]
            st.dataframe(hoy[['socio_id', 'hora']], use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("🆕 Alta Socio / 💰 Abono")
            # Formulario simplificado para evitar errores de conexión
            with st.form("gestion_admin"):
                n = st.text_input("Nombre")
                a = st.text_input("Apellido")
                s = st.number_input("Clases", value=8)
                if st.form_submit_button("Guardar"):
                    nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "saldo_clases": s}])
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=pd.concat([df_s, nuevo], ignore_index=True))
                    st.success("¡Guardado!")
                    st.rerun()
    else:
        st.info("Ingresá la clave 'Samuel28' para administrar.")
