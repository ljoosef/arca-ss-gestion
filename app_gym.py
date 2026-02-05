import streamlit as st
import pandas as pd
import os

# CONFIGURACIÓN DE LINKS PÚBLICOS (Los que no fallan)
URL_BASE = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv"
URL_SOCIOS = f"{URL_BASE}&gid=0"
URL_RESERVAS = f"{URL_BASE}&gid=1298454736"

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Vista Alumnos", "Administración 🔒"])

# --- FUNCIÓN PARA CARGAR DATOS ---
def cargar_datos_seguro():
    try:
        df_s = pd.read_csv(URL_SOCIOS)
        df_r = pd.read_csv(URL_RESERVAS)
        # Limpieza de columnas
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- MODO ALUMNOS ---
if modo == "Vista Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    df_socios, df_reservas = cargar_datos_seguro()
    
    if not df_socios.empty:
        alumno = st.selectbox("Seleccioná tu nombre", [""] + df_socios['nombre'].tolist())
        if alumno:
            # Buscar saldo
            datos = df_socios[df_socios['nombre'] == alumno].iloc[0]
            st.info(f"Hola **{alumno}**. Clases restantes: **{datos['saldo_clases']}**")
            
            fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                st.balloons()
                st.success(f"¡Tu horario está confirmado! En caso de que no puedas asistir, ¡avisanos!")
                st.info(f"Reservado: {fec} a las {hor} hs. (Avisale a Sofía por WhatsApp)")
    else:
        st.error("Error al cargar la base de datos.")

# --- MODO ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Control")
    # Clave con asteriscos
    clave_ingresada = st.sidebar.text_input("Ingresá la clave", type="password")
    
    if clave_ingresada == "Samuel28": # Tu clave elegida
        df_s, df_r = cargar_datos_seguro()
        
        tab1, tab2 = st.tabs(["📅 Turnos de Hoy", "👥 Lista de Socios"])
        
        with tab1:
            dia_ver = st.date_input("Ver agenda del día:", value=pd.to_datetime("today"))
            turnos_dia = df_r[df_r['fecha'] == str(dia_ver)]
            if not turnos_dia.empty:
                st.write(f"Alumnos anotados para el {dia_ver}:")
                st.dataframe(turnos_dia[['socio_id', 'hora']], use_container_width=True)
            else:
                st.write("No hay reservas aún.")
                
        with tab2:
            st.subheader("Estado de Alumnos")
            st.table(df_s[['nombre', 'saldo_clases', 'vencimiento']])
    else:
        st.warning("🔒 Área restringida. Ingresá la clave en el panel lateral.")
