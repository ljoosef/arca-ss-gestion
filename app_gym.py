import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# CONFIGURACIÓN
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Estética para que se vea profesional en el celu
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 10px; height: 3em; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# Conector oficial (ahora usará los Secrets automáticamente)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # ttl=0 para que siempre traiga lo último si Sofía edita el Excel a mano
        df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
        df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- INTERFAZ PRINCIPAL ---
st.title("🏋️ Arca S&S")
menu = st.radio("Seleccioná:", ["Soy Alumno", "Administración 🔒"], horizontal=True)
st.write("---")

df_s, df_r = cargar_datos()

if menu == "Soy Alumno":
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    if not df_s.empty:
        df_s['full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Buscá tu nombre:", [""] + df_s['full'].tolist())
        
        if alumno:
            idx = df_s[df_s['full'] == alumno].index[0]
            saldo = int(df_s.at[idx, 'saldo_clases'])
            st.info(f"Hola **{alumno}**. Te quedan **{saldo}** clases.")
            
            if saldo > 0:
                fec = st.date_input("Día de entrenamiento")
                hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR MI TURNO"):
                    # 1. Registrar reserva
                    nueva_res = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                    df_r_act = pd.concat([df_r, nueva_res], ignore_index=True)
                    conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_r_act)
                    
                    # 2. Descontar clase
                    df_s.at[idx, 'saldo_clases'] = saldo - 1
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s.drop(columns=['full']))
                    
                    st.balloons()
                    st.success("¡Turno guardado! Te esperamos.")
                    st.rerun()

else:
    clave = st.text_input("Clave de Acceso:", type="password")
    if clave == "Samuel28":
        t1, t2, t3 = st.tabs(["📅 Agenda", "👥 Socios", "➕ Acciones"])
        
        with t1:
            dia = st.date_input("Ver turnos del día:", value=pd.to_datetime("today"))
            if not df_r.empty:
                hoy = df_r[df_r['fecha'] == str(dia)]
                st.dataframe(hoy[['socio_id', 'hora']], use_container_width=True, hide_index=True)

        with t2:
            st.dataframe(df_s[['nombre', 'apellido', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)

        with t3:
            st.subheader("Cargar Nuevo Socio o Pack")
            with st.form("alta"):
                n = st.text_input("Nombre")
                a = st.text_input("Apellido")
                s = st.number_input("Cantidad de Clases", value=8)
                v = st.date_input("Vencimiento del pack")
                if st.form_submit_button("GUARDAR EN SISTEMA"):
                    nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "saldo_clases": s, "vencimiento": str(v), "contacto": "-"}])
                    df_final = pd.concat([df_s, nuevo], ignore_index=True)
                    # AQUÍ SE USA LA LLAVE JSON PARA ESCRIBIR
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_final)
                    st.success(f"¡Socio {n} cargado correctamente!")
                    st.rerun()
