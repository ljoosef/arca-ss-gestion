import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# --- CONFIGURACIÓN ---
# ID de tu planilla
SHEET_ID = "1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0"

# URLs de Lectura Directa (INFALIBLES si el Excel está "Público -> Lector")
# gid=0 suele ser la primera hoja (Socios). Si no te carga, revisaremos este número.
URL_SOCIOS_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# gid de reservas (usamos el que tenías antes, si falla lo corregimos)
URL_RESERVAS_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1298454736"

# Celular de Sofía para respaldo
CELULAR_ADMIN = "549XXXXXXXXXX" 

st.set_page_config(page_title="Arca S&S", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Intentamos conexión segura SOLO para escritura (si falla, no rompe la app)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

def cargar_datos_seguro():
    try:
        # Intentamos leer por la vía rápida (CSV Público)
        df_s = pd.read_csv(URL_SOCIOS_CSV)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        
        try:
            df_r = pd.read_csv(URL_RESERVAS_CSV)
            df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        except:
            df_r = pd.DataFrame(columns=['socio_id', 'fecha', 'hora'])
            
        return df_s, df_r
    except Exception as e:
        st.error(f"⚠️ No pude leer el Excel. Asegurate de que esté en 'Cualquiera con el enlace -> Lector'. Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- INTERFAZ ---
st.title("🏋️ Arca S&S")
menu = st.radio("Menú:", ["Soy Alumno", "Administración 🔒"], horizontal=True)
st.write("---")

df_s, df_r = cargar_datos_seguro()

# --- VISTA ALUMNO ---
if menu == "Soy Alumno":
    if not df_s.empty:
        # Creamos columna nombre completo
        if 'nombre' in df_s.columns and 'apellido' in df_s.columns:
            df_s['full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
            alumno = st.selectbox("Buscá tu nombre:", [""] + df_s['full'].tolist())
            
            if alumno:
                idx = df_s[df_s['full'] == alumno].index[0]
                saldo = int(df_s.at[idx, 'saldo_clases'])
                st.info(f"👋 Hola **{alumno}**. Te quedan **{saldo}** clases.")
                
                if saldo > 0:
                    fec = st.date_input("Fecha")
                    hor = st.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                    
                    if st.button("CONFIRMAR ASISTENCIA"):
                        # Intentamos guardar automático
                        try:
                            # Preparar datos
                            nueva_res = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                            df_r_act = pd.concat([df_r, nueva_res], ignore_index=True)
                            
                            df_s.at[idx, 'saldo_clases'] = saldo - 1
                            df_subir = df_s.drop(columns=['full'])
                            
                            # Intento de escritura con la llave
                            conn.update(spreadsheet=SHEET_ID, worksheet="Reservas", data=df_r_act)
                            conn.update(spreadsheet=SHEET_ID, worksheet="Socios", data=df_subir)
                            st.balloons()
                            st.success("¡Reserva Guardada Automáticamente!")
                            st.rerun()
                        except:
                            # PLAN B: WhatsApp (Si falla la llave, usamos esto)
                            msg = f"Hola Sofi! Soy {alumno}. Voy el {fec} a las {hor}. (Descontame 1 clase, me quedan {saldo-1})"
                            link = f"https://wa.me/{CELULAR_ADMIN}?text={urllib.parse.quote(msg)}"
                            st.warning("⚠️ No se pudo guardar automático (Error de conexión).")
                            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;text-align:center;border-radius:5px;">📲 CONFIRMAR POR WHATSAPP</div></a>', unsafe_allow_html=True)
        else:
            st.error("No encuentro las columnas 'nombre' y 'apellido' en el Excel.")
            st.write("Columnas encontradas:", df_s.columns.tolist())

# --- VISTA ADMIN ---
else:
    if st.text_input("Clave:", type="password") == "Samuel28":
        t1, t2 = st.tabs(["Socios", "Cargar Nuevo"])
        with t1:
            if not df_s.empty:
                st.dataframe(df_s, hide_index=True)
        with t2:
            st.write("Para cargar nuevo socio:")
            n = st.text_input("Nombre"); a = st.text_input("Apellido")
            s = st.number_input("Clases", value=8); v = st.date_input("Vence")
            if st.button("GENERAR ALTA"):
                msg = f"ALTA NUEVA: {n} {a}, Pack {s} clases, Vence {v}"
                link = f"https://wa.me/{CELULAR_ADMIN}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank">📲 ENVIAR ALTA POR WHATSAPP</a>', unsafe_allow_html=True)
