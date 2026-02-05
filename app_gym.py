import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import os

# --- CONFIGURACIÓN ---
# Usamos el link público para LEER (así nunca falla la lectura)
URL_LECTURA_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"
URL_LECTURA_RESERVAS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

# Link privado para intentar escribir (si falla, usamos WhatsApp)
URL_ESCRITURA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

# IMPORTANTE: CAMBIAR POR EL NÚMERO DE SOFÍA O EL TUYO
CELULAR_ADMIN = "5491100000000" 

st.set_page_config(page_title="Arca S&S", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Intentamos inicializar la conexión oficial (por si los secrets reviven)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# --- FUNCIÓN DE LECTURA SEGURA ---
def leer_datos():
    try:
        # Leemos directo del CSV público (Infalible)
        df_s = pd.read_csv(URL_LECTURA_SOCIOS)
        df_r = pd.read_csv(URL_LECTURA_RESERVAS)
        
        # Limpiamos columnas
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- FUNCIÓN DE ESCRITURA INTELIGENTE ---
def intentar_guardar(df_socios_nuevo, df_reservas_nuevo, mensaje_whatsapp):
    try:
        # Paso 1: Intentamos escribir en Drive
        if conn:
            conn.update(spreadsheet=URL_ESCRITURA, worksheet="Reservas", data=df_reservas_nuevo)
            conn.update(spreadsheet=URL_ESCRITURA, worksheet="Socios", data=df_socios_nuevo)
            st.balloons()
            st.success("¡Guardado en el Sistema Exitosamente!")
            st.rerun()
        else:
            raise Exception("Sin conexión")
    except:
        # Paso 2: Si falla, Plan B (WhatsApp)
        st.warning("⚠️ El sistema de guardado automático no está disponible.")
        st.info("👇 Tocá este botón para enviar la confirmación a Sofía y que ella lo registre:")
        
        texto_encoded = urllib.parse.quote(mensaje_whatsapp)
        link = f"https://wa.me/{CELULAR_ADMIN}?text={texto_encoded}"
        
        st.markdown(f'''
            <a href="{link}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366;color:white;padding:15px;text-align:center;border-radius:10px;font-size:18px;font-weight:bold;margin-top:10px;">
                    📱 ENVIAR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- INTERFAZ ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Vista Alumnos", "Administración 🔒"])

df_s, df_r = leer_datos()

# VISTA ALUMNOS
if modo == "Vista Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"): st.image("logo.png", width=120)

    if not df_s.empty:
        df_s['nombre_full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Tu nombre:", [""] + df_s['nombre_full'].tolist())
        
        if alumno:
            idx = df_s[df_s['nombre_full'] == alumno].index[0]
            saldo = df_s.at[idx, 'saldo_clases']
            st.info(f"Hola **{alumno}**. Clases disponibles: **{int(saldo)}**")
            
            if saldo > 0:
                fec = st.date_input("Fecha", min_value=pd.to_datetime("today"))
                hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("RESERVAR LUGAR", use_container_width=True):
                    # Preparamos los datos por si funciona el guardado automático
                    nueva_r = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                    df_r_new = pd.concat([df_r, nueva_r], ignore_index=True)
                    
                    df_s.at[idx, 'saldo_clases'] = saldo - 1
                    df_s_new = df_s.drop(columns=['nombre_full'])
                    
                    msg = f"Hola Sofi! Soy {alumno}. Reservo para el {fec} a las {hor}. (Me quedan {saldo-1} clases)"
                    intentar_guardar(df_s_new, df_r_new, msg)

# VISTA ADMIN
else:
    st.title("🛡️ Gestión")
    if st.sidebar.text_input("Clave", type="password") == "Samuel28":
        tab1, tab2, tab3 = st.tabs(["Agenda", "Socios", "Acciones"])
        
        with tab1:
            dia = st.date_input("Día:", value=pd.to_datetime("today"))
            if not df_r.empty:
                st.dataframe(df_r[df_r['fecha'] == str(dia)][['socio_id', 'hora']], hide_index=True, use_container_width=True)
        
        with tab2:
            if not df_s.empty:
                st.dataframe(df_s[['nombre', 'apellido', 'saldo_clases', 'vencimiento']], hide_index=True, use_container_width=True)
        
        with tab3:
            st.write("### Gestión Manual")
            with st.form("admin"):
                n = st.text_input("Nombre"); a = st.text_input("Apellido")
                s = st.number_input("Clases", 8)
                if st.form_submit_button("Cargar Socio"):
                    nuevo = pd.DataFrame([{"nombre": n, "apellido": a, "saldo_clases": s, "contacto": "-", "vencimiento": "2026-12-31"}])
                    df_s_new = pd.concat([df_s, nuevo], ignore_index=True)
                    msg = f"NUEVO SOCIO: {n} {a} - Clases: {s}"
                    intentar_guardar(df_s_new, df_r, msg)
