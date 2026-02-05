import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# --- 1. CONFIGURACIÓN (Tus datos) ---
SHEET_ID = "1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0"
URL_SOCIOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Si creaste la pestaña Reservas nueva, el gid suele ser distinto. 
# Si esta línea falla, probá cambiar el gid por '0' temporalmente o buscá el gid correcto en la URL de tu navegador.
URL_RESERVAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1298454736"

CELULAR_ADMIN = "549299XXXXXXX" # <--- Poné tu celu acá

st.set_page_config(page_title="Arca S&S", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS (Lectura Infalible) ---
def cargar_datos():
    try:
        # Leemos Socios
        df_s = pd.read_csv(URL_SOCIOS)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        
        # Leemos Reservas (Si falla, crea una vacía para no romper la app)
        try:
            df_r = pd.read_csv(URL_RESERVAS)
            df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        except:
            df_r = pd.DataFrame(columns=['fecha', 'hora', 'socio_id'])
            
        return df_s, df_r
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- 3. INTERFAZ ---
st.title("🏋️ Arca S&S")
menu = st.radio("Menú:", ["Soy Alumno", "Administración 🔒"], horizontal=True)
st.write("---")

df_s, df_r = cargar_datos()

# --- A. VISTA ALUMNO ---
if menu == "Soy Alumno":
    if not df_s.empty and 'nombre' in df_s.columns:
        df_s['full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        alumno = st.selectbox("Buscá tu nombre:", [""] + df_s['full'].tolist())
        
        if alumno:
            idx = df_s[df_s['full'] == alumno].index[0]
            saldo = int(df_s.at[idx, 'saldo_clases'])
            st.info(f"Hola **{alumno}**. Te quedan **{saldo}** clases.")
            
            if saldo > 0:
                c1, c2 = st.columns(2)
                fec = c1.date_input("Fecha")
                hor = c2.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("RESERVAR CLASE"):
                    msg = f"Hola! Soy {alumno}. Reservo para el {fec} a las {hor}. (Me quedan {saldo-1} clases)"
                    link = f"https://wa.me/{CELULAR_ADMIN}?text={urllib.parse.quote(msg)}"
                    st.success("¡Reserva lista!")
                    st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;text-align:center;border-radius:8px;">📲 CONFIRMAR POR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- B. VISTA ADMINISTRADOR (MEJORADA) ---
else:
    clave = st.text_input("Ingresá la clave:", type="password")
    if clave == "Samuel28":
        # Creamos 3 pestañas claras
        tab1, tab2, tab3 = st.tabs(["📅 AGENDA DE RESERVAS", "👥 LISTADO DE ALUMNOS", "➕ NUEVO ALUMNO"])
        
        # PESTAÑA 1: Quién reservó (Lo que pediste)
        with tab1:
            st.subheader("Turnos Reservados")
            if not df_r.empty:
                # Ordenamos por fecha para que veas lo próximo primero
                try:
                    df_r = df_r.sort_values(by=['fecha', 'hora'], ascending=False)
                    st.dataframe(df_r[['fecha', 'hora', 'socio_id']], use_container_width=True, hide_index=True)
                except:
                    st.write(df_r) # Muestra crudo si falla el orden
            else:
                st.info("No hay reservas cargadas todavía en la hoja 'Reservas'.")

        # PESTAÑA 2: Tus alumnos y sus saldos
        with tab2:
            st.subheader("Estado de Cuenta de Alumnos")
            if not df_s.empty:
                # Mostramos solo lo importante
                cols_ver = ['nombre', 'apellido', 'saldo_clases', 'vencimiento']
                # Filtramos columnas que existan para evitar errores
                cols_final = [c for c in cols_ver if c in df_s.columns]
                st.dataframe(df_s[cols_final], use_container_width=True, hide_index=True)
            else:
                st.warning("No se pudo leer la lista de alumnos.")

        # PESTAÑA 3: Cargar gente nueva
        with tab3:
            st.write("Dar de alta o renovar pack:")
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            s = st.number_input("Cantidad de Clases", value=8)
            v = st.date_input("Fecha de Vencimiento")
            
            if st.button("GENERAR ALTA"):
                msg = f"ALTA: {n} {a} - Pack: {s} clases - Vence: {v}"
                link = f"https://wa.me/{CELULAR_ADMIN}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;text-align:center;border-radius:8px;">📲 ENVIAR ALTA A SOFÍA</div></a>', unsafe_allow_html=True)
