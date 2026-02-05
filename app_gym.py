import streamlit as st
import pandas as pd
import os

# LINKS DIRECTOS DE TU PLANILLA (Exportados como CSV)
# Estos links leen la info directo sin pedir permiso de API
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"
URL_RESERVAS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Estética
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

def cargar_datos():
    try:
        # Leemos los CSV directamente
        df_s = pd.read_csv(URL_SOCIOS)
        df_r = pd.read_csv(URL_RESERVAS)
        # Limpieza de columnas
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except Exception as e:
        st.error(f"Error al conectar con la base: {e}")
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
        # Crear nombre completo
        df_s['nombre_full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Seleccioná tu nombre", [""] + df_s['nombre_full'].tolist())
        
        if alumno:
            datos_alumno = df_s[df_s['nombre_full'] == alumno].iloc[0]
            saldo = datos_alumno['saldo_clases']
            st.info(f"Hola **{alumno}**. Tenés **{int(saldo)}** clases restantes.")
            
            fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                st.balloons()
                st.success(f"¡Tu horario está confirmado! En caso de que no puedas asistir, ¡avisanos!")
                st.info("Avisale a Sofía por WhatsApp para que descuente tu clase.")
    else:
        st.warning("Cargando base de datos...")

# --- VISTA ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Control")
    clave = st.sidebar.text_input("Clave Admin", type="password")
    
    if clave == "Samuel28":
        df_s, df_r = cargar_datos()
        tab1, tab2 = st.tabs(["📅 Agenda de Hoy", "👥 Lista de Socios"])

        with tab1:
            dia = st.date_input("Ver turnos de:", value=pd.to_datetime("today"))
            if not df_r.empty:
                # Filtrar por fecha (asegurando que coincidan formatos)
                hoy = df_r[df_r['fecha'] == str(dia)]
                if not hoy.empty:
                    st.dataframe(hoy[['socio_id', 'hora']], use_container_width=True, hide_index=True)
                else:
                    st.write("No hay reservas para este día.")

        with tab2:
            st.subheader("Estado de Socios")
            if not df_s.empty:
                # Formatear fecha de vencimiento (DD/MM/AAAA)
                df_vis = df_s.copy()
                try:
                    df_vis['vencimiento'] = pd.to_datetime(df_vis['vencimiento']).dt.strftime('%d/%m/%Y')
                except: pass
                st.dataframe(df_vis[['nombre', 'apellido', 'contacto', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)
    else:
        st.info("Ingresá la clave 'Samuel28' para administrar.")
