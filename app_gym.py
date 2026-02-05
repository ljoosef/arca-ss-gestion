import streamlit as st
import pandas as pd
import os

# CONFIGURACIÓN DE LINKS PÚBLICOS
URL_BASE = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv"
URL_SOCIOS = f"{URL_BASE}&gid=0"
URL_RESERVAS = f"{URL_BASE}&gid=1298454736"

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Vista Alumnos", "Administración 🔒"])

def cargar_datos_seguro():
    try:
        df_s = pd.read_csv(URL_SOCIOS)
        df_r = pd.read_csv(URL_RESERVAS)
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
    
    df_socios, _ = cargar_datos_seguro()
    
    if not df_socios.empty:
        # Combinamos nombre y apellido para el selector si existen ambas columnas
        if 'apellido' in df_socios.columns:
            df_socios['nombre_full'] = df_socios['nombre'] + " " + df_socios['apellido']
        else:
            df_socios['nombre_full'] = df_socios['nombre']
            
        alumno = st.selectbox("Seleccioná tu nombre", [""] + df_socios['nombre_full'].tolist())
        
        if alumno:
            datos = df_socios[df_socios['nombre_full'] == alumno].iloc[0]
            st.info(f"Hola **{alumno}**. Clases restantes: **{datos['saldo_clases']}**")
            
            fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                st.balloons()
                st.success(f"¡Tu horario está confirmado! En caso de que no puedas asistir, ¡avisanos!")
    else:
        st.error("Error al cargar datos.")

# --- MODO ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Control")
    clave_ingresada = st.sidebar.text_input("Ingresá la clave", type="password")
    
    if clave_ingresada == "Samuel28":
        df_s, df_r = cargar_datos_seguro()
        
        tab1, tab2 = st.tabs(["📅 Turnos de Hoy", "👥 Lista de Socios"])
        
        with tab1:
            dia_ver = st.date_input("Ver agenda del día:", value=pd.to_datetime("today"))
            if not df_r.empty:
                turnos_dia = df_r[df_r['fecha'] == str(dia_ver)]
                if not turnos_dia.empty:
                    st.dataframe(turnos_dia[['socio_id', 'hora']], use_container_width=True, hide_index=True)
                else:
                    st.write("No hay reservas aún para este día.")
            else:
                st.write("No hay datos de reservas.")
                
        with tab2:
            st.subheader("Estado Detallado de Alumnos")
            if not df_s.empty:
                # Procesamiento de fechas y columnas
                df_s['vencimiento'] = pd.to_datetime(df_s['vencimiento'])
                df_s = df_s.sort_values(by='vencimiento')
                
                df_mostrar = df_s.copy()
                df_mostrar['vencimiento'] = df_mostrar['vencimiento'].dt.strftime('%d/%m/%Y')
                
                # Definimos las columnas a mostrar (asegurando que existan)
                cols_ok = [c for c in ['nombre', 'apellido', 'contacto', 'saldo_clases', 'vencimiento'] if c in df_mostrar.columns]
                tabla_final = df_mostrar[cols_ok]
                
                st.dataframe(tabla_final, use_container_width=True, hide_index=True)
            else:
                st.write("No hay socios cargados.")
    else:
        st.warning("🔒 Área restringida. Ingresá la clave en el panel lateral.")
