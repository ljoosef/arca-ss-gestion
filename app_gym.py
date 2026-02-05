import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# Ocultar menús para estética de App
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Conexión oficial
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
    df_s.columns = [str(c).strip().lower() for c in df_s.columns]
    df_r.columns = [str(c).strip().lower() for c in df_r.columns]
    return df_s, df_r

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Reservas Alumnos", "Administración 🔒"])

# --- VISTA ALUMNOS ---
if modo == "Reservas Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    df_s, df_r = cargar_datos()
    df_s['nombre_full'] = df_s['nombre'] + " " + df_s['apellido']
    
    alumno = st.selectbox("Seleccioná tu nombre", [""] + df_s['nombre_full'].tolist())
    
    if alumno:
        idx = df_s[df_s['nombre_full'] == alumno].index[0]
        saldo = df_s.at[idx, 'saldo_clases']
        st.info(f"Hola **{alumno}**. Clases restantes: **{saldo}**")
        
        if saldo > 0:
            fec = st.date_input("Fecha de clase", min_value=pd.to_datetime("today"))
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR TURNO", use_container_width=True):
                # 1. Guardar Reserva
                nueva_r = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                df_r_act = pd.concat([df_r, nueva_r], ignore_index=True)
                conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_r_act)
                
                # 2. Descontar Saldo
                df_s.at[idx, 'saldo_clases'] = saldo - 1
                conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s.drop(columns=['nombre_full']))
                
                st.balloons()
                st.success("¡Tu horario está confirmado! En caso de que no puedas asistir, ¡avisanos!")
                st.rerun()
        else:
            st.error("No te quedan clases. Contactá a Sofía para renovar.")

# --- VISTA ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Gestión")
    clave = st.sidebar.text_input("Clave de Acceso", type="password")
    
    if clave == "Samuel28":
        df_s, df_r = cargar_datos()
        tab1, tab2, tab3 = st.tabs(["📅 Agenda", "👥 Socios", "🛠️ Acciones"])

        with tab1:
            dia = st.date_input("Día a consultar:", value=pd.to_datetime("today"))
            hoy = df_r[df_r['fecha'] == str(dia)]
            st.dataframe(hoy[['socio_id', 'hora']], use_container_width=True, hide_index=True)

        with tab2:
            df_s_v = df_s.copy()
            df_s_v['vencimiento'] = pd.to_datetime(df_s_v['vencimiento']).dt.strftime('%d/%m/%Y')
            st.dataframe(df_s_v[['nombre', 'apellido', 'contacto', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🆕 Alta Socio")
                with st.form("alta_form"):
                    n = st.text_input("Nombre")
                    a = st.text_input("Apellido")
                    c = st.text_input("Contacto")
                    s = st.number_input("Clases", value=8)
                    v = st.date_input("Vencimiento")
                    if st.form_submit_button("Guardar"):
                        nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "contacto": c, "saldo_clases": s, "vencimiento": str(v)}])
                        conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=pd.concat([df_s, nuevo], ignore_index=True))
                        st.success("¡Socio Creado!")

            with col2:
                st.subheader("💰 Cargar Abono")
                s_sel = st.selectbox("Socio", df_s['nombre'].tolist())
                clases_plus = st.number_input("Sumar clases", value=8)
                ven_nuevo = st.date_input("Nuevo Vencimiento")
                if st.button("Actualizar"):
                    df_s.loc[df_s['nombre'] == s_sel, 'saldo_clases'] += clases_plus
                    df_s.loc[df_s['nombre'] == s_sel, 'vencimiento'] = str(ven_nuevo)
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s)
                    st.success("¡Abono cargado!")
    else:
        st.info("Área protegida. Ingresá la clave en el panel lateral.")
