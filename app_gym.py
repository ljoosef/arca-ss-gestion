import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# CONFIGURACIÓN
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"
CUPO_MAXIMO = 8

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Navegación:", ["Vista Alumnos", "Panel de Administración 🔒"])

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
    return df_s, df_r

# --- MODO ALUMNOS ---
if modo == "Vista Alumnos":
    st.title("🏋️ Arca S&S - Reservas")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    try:
        df_socios, df_reservas = cargar_datos()
        alumno = st.selectbox("Seleccioná tu nombre", [""] + df_socios['nombre'].tolist())
        
        if alumno:
            datos = df_socios[df_socios['nombre'] == alumno].iloc[0]
            st.info(f"Hola **{alumno}**. Clases restantes: **{datos['clases_restantes']}**")
            
            fec = st.date_input("Día de entrenamiento", min_value=pd.to_datetime("today"))
            
            # --- LÓGICA DE CUPOS ---
            horarios_todos = ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"]
            horarios_disponibles = []

            for h in horarios_todos:
                conteo = len(df_reservas[(df_reservas['fecha'] == str(fec)) & (df_reservas['hora'] == h)])
                if conteo < CUPO_MAXIMO:
                    horarios_disponibles.append(f"{h} ({CUPO_MAXIMO - conteo} lugares)")

            if horarios_disponibles:
                hor_seleccionado = st.selectbox("Horarios con lugar:", horarios_disponibles)
                hora_limpia = hor_seleccionado.split(" ")[0]

                if st.button("CONFIRMAR TURNO", use_container_width=True):
                    _, df_r_check = cargar_datos()
                    conteo_final = len(df_r_check[(df_r_check['fecha'] == str(fec)) & (df_r_check['hora'] == hora_limpia)])
                    
                    if conteo_final < CUPO_MAXIMO:
                        # Guardar Reserva
                        nueva = pd.DataFrame([{"id": len(df_r_check)+1, "socio_id": alumno, "fecha": str(fec), "hora": hora_limpia}])
                        df_final = pd.concat([df_r_check, nueva], ignore_index=True)
                        conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_final)
                        
                        # Descontar clase
                        df_socios.loc[df_socios['nombre'] == alumno, 'clases_restantes'] -= 1
                        conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_socios)
                        
                        st.balloons()
                        # MENSAJE DE CONFIRMACIÓN SOLICITADO
                        st.success(f"¡Tu horario está confirmado! En caso de que no puedas asistir, ¡avisanos!")
                        st.info(f"Reservado: {fec} a las {hora_limpia} hs.")
                    else:
                        st.error("Cupo completado. Por favor, elegí otro horario.")
            else:
                st.error("No hay más cupos disponibles para este día.")
    except Exception as e:
        st.warning("Cargando datos...")

# --- MODO ADMINISTRADOR ---
else:
    st.title("🛡️ Gestión Arca S&S")
    password = st.sidebar.text_input("Clave Samuel28", type="password")
    
    if password == "admin123":
        tab1, tab2, tab3 = st.tabs(["📅 Agenda", "👥 Socios", "➕ Alta/Abonos"])
        df_s, df_r = cargar_datos()

        with tab1:
            st.subheader("Control de Asistencia")
            filtro_fecha = st.date_input("Ver turnos del día:", value=pd.to_datetime("today"))
            turnos_hoy = df_r[df_r['fecha'] == str(filtro_fecha)]
            
            if not turnos_hoy.empty:
                for h in sorted(["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"]):
                    alumnos_hora = turnos_hoy[turnos_hoy['hora'] == h]['socio_id'].tolist()
                    if alumnos_hora:
                        with st.expander(f"⏰ {h} hs - ({len(alumnos_hora)}/{CUPO_MAXIMO})"):
                            for a in alumnos_hora:
                                # Buscar datos del socio para mostrar detalle
                                socio_info = df_s[df_s['nombre'] == a].iloc[0]
                                st.write(f"👤 **{a}** | 📱 {socio_info['celular']} | 🔋 Saldo: {socio_info['clases_restantes']}")
            else:
                st.write("No hay reservas para esta fecha.")

        with tab2:
            st.subheader("Base de Datos de Socios")
            st.dataframe(df_s[['nombre', 'celular', 'clases_restantes']], use_container_width=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Nuevo Socio")
                with st.form("alta"):
                    n = st.text_input("Nombre")
                    c = st.text_input("Celular")
                    p = st.number_input("Pack Inicial", value=8)
                    if st.form_submit_button("Dar de Alta"):
                        df_up = pd.concat([df_s, pd.DataFrame([{"nombre": n, "celular": c, "clases_restantes": p}])], ignore_index=True)
                        conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_up)
                        st.success(f"{n} agregado.")
            with col2:
                st.subheader("Cargar Abono")
                s_sel = st.selectbox("Socio", df_s['nombre'].tolist())
                c_sumar = st.number_input("Sumar clases", value=8)
                if st.button("Acreditar Clases"):
                    df_s.loc[df_s['nombre'] == s_sel, 'clases_restantes'] += c_sumar
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s)
                    st.success(f"Saldo actualizado para {s_sel}")
    else:
        st.info("Ingresá la clave 'admin123' en el panel lateral.")
