import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ID de tu planilla (Más seguro que el link)
SHEET_ID = "1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0"

st.set_page_config(page_title="Arca S&S", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Leemos los datos CRUDOS para ver las columnas exactas
        df_s = conn.read(spreadsheet=SHEET_ID, worksheet="Socios", ttl=0)
        try:
            df_r = conn.read(spreadsheet=SHEET_ID, worksheet="Reservas", ttl=0)
        except:
            df_r = pd.DataFrame()
        return df_s, df_r
    except Exception as e:
        st.error(f"Error leyendo Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()

st.title("🏋️ Arca S&S")
menu = st.radio("Perfil:", ["Alumno", "Admin 🔒"], horizontal=True)
st.write("---")

df_s, df_r = cargar_datos()

# --- LÓGICA INTELIGENTE PARA COLUMNAS ---
# Detectamos automáticamente cómo se llaman tus columnas para no fallar
if not df_s.empty:
    cols = df_s.columns.tolist()
    # Asumimos el orden: Nombre, Apellido, Contacto, Saldo, Vencimiento
    # Si tu excel tiene otro orden, avisa.
    col_nombre = cols[0]
    col_apellido = cols[1] 
    col_saldo = cols[3]
else:
    st.error("El Excel 'Socios' está vacío o no se puede leer.")
    st.stop()

# --- VISTA ALUMNO ---
if menu == "Alumno":
    # Creamos nombre completo para el buscador
    df_s['BUSCADOR'] = df_s[col_nombre].astype(str) + " " + df_s[col_apellido].astype(str)
    alumno = st.selectbox("Tu nombre:", [""] + df_s['BUSCADOR'].tolist())
    
    if alumno:
        idx = df_s[df_s['BUSCADOR'] == alumno].index[0]
        saldo = int(df_s.at[idx, col_saldo])
        st.info(f"Hola. Te quedan **{saldo}** clases.")
        
        if saldo > 0:
            c1, c2 = st.columns(2)
            fec = c1.date_input("Fecha")
            hor = c2.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("RESERVAR"):
                # Guardar Reserva
                nueva_r = pd.DataFrame([{"socio_id": alumno, "fecha": str(fec), "hora": hor}])
                df_r_final = pd.concat([df_r, nueva_r], ignore_index=True)
                conn.update(spreadsheet=SHEET_ID, worksheet="Reservas", data=df_r_final)
                
                # Descontar y Guardar Socio
                df_s.at[idx, col_saldo] = saldo - 1
                # Borramos la columna temporal 'BUSCADOR' antes de subir para que Google no rechace
                df_subir = df_s.drop(columns=['BUSCADOR'])
                conn.update(spreadsheet=SHEET_ID, worksheet="Socios", data=df_subir)
                
                st.success("✅ ¡Reserva guardada!")
                st.rerun()

# --- VISTA ADMIN ---
else:
    if st.text_input("Clave:", type="password") == "Samuel28":
        t1, t2, t3 = st.tabs(["Agenda", "Socios", "Alta"])
        
        with t1:
            st.dataframe(df_r, use_container_width=True)
        with t2:
            st.dataframe(df_s, use_container_width=True)
        with t3:
            st.write("Nuevo Alumno:")
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            s = st.number_input("Clases", value=8)
            v = st.date_input("Vencimiento")
            
            if st.button("GUARDAR EN EXCEL"):
                # Usamos los nombres EXACTOS de las columnas que leímos del Excel
                nuevo_dato = {
                    cols[0]: n,   # Nombre
                    cols[1]: a,   # Apellido
                    cols[2]: "-", # Contacto
                    cols[3]: s,   # Saldo
                    cols[4]: str(v) # Vencimiento
                }
                
                df_nuevo = pd.DataFrame([nuevo_dato])
                
                # Limpiamos df_s de la columna buscador antes de unir
                df_limpio = df_s.drop(columns=['BUSCADOR']) if 'BUSCADOR' in df_s.columns else df_s
                
                df_final = pd.concat([df_limpio, df_nuevo], ignore_index=True)
                
                conn.update(spreadsheet=SHEET_ID, worksheet="Socios", data=df_final)
                st.success("✅ ¡Guardado!")
                st.rerun()
