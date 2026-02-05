import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA - Asegúrate de que sea esta
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# Conector para lectura y escritura
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
    df_s.columns = [str(c).strip().lower() for c in df_s.columns]
    df_r.columns = [str(c).strip().lower() for c in df_r.columns]
    return df_s, df_r

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Navegación:", ["Vista Alumnos", "Administración 🔒"])

# --- MODO ALUMNOS ---
if modo == "Vista Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    df_s, df_r = cargar_datos()
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
                # Guardar reserva y descontar clase automáticamente
                nueva_res = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                df_r_act = pd.concat([df_r, nueva_res], ignore_index=True)
                conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_r_act)
                
                df_s.at[idx, 'saldo_clases'] = saldo - 1
                conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s.drop(columns=['nombre_full']))
                
                st.balloons()
                st.success("¡Turno confirmado!")
                st.rerun()

# --- MODO ADMINISTRADOR ---
else:
    st.title("🛡️ Panel de Gestión")
    clave = st.sidebar.text_input("Clave Admin", type="password")
    
    if clave == "Samuel28":
        df_s, df_r = cargar_datos()
        tab1, tab2, tab3 = st.tabs(["📅 Agenda", "👥 Socios", "⚙️ Acciones"])

        with tab1:
            dia = st.date_input("Turnos del día:", value=pd.to_datetime("today"))
            hoy = df_r[df_r['fecha'] == str(dia)]
            st.dataframe(hoy[['socio_id', 'hora']], use_container_width=True, hide_index=True)

        with tab2:
            df_vis = df_s.copy()
            st.dataframe(df_vis[['nombre', 'apellido', 'contacto', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🆕 Alta de Socio")
                with st.form("alta"):
                    n, a, c = st.text_input("Nombre"), st.text_input("Apellido"), st.text_input("Celular")
                    s, v = st.number_input("Clases", value=8), st.date_input("Vencimiento")
                    if st.form_submit_button("Guardar"):
                        nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "contacto": c, "saldo_clases": s, "vencimiento": str(v)}])
                        conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=pd.concat([df_s, nuevo], ignore_index=True))
                        st.success("¡Socio creado!")
                        st.rerun()

            with col2:
                st.subheader("💰 Cargar Abono")
                s_sel = st.selectbox("Socio", df_s['nombre'].tolist())
                plus = st.number_input("Sumar clases", value=8)
                ven_n = st.date_input("Nuevo Vencimiento")
                if st.button("Actualizar"):
                    df_s.loc[df_s['nombre'] == s_sel, 'saldo_clases'] += plus
                    df_s.loc[df_s['nombre'] == s_sel, 'vencimiento'] = str(ven_n)
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s)
                    st.success("¡Abono actualizado!")
                    st.rerun()
    else:
        st.info("Ingresá la clave para gestionar.")
