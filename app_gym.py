import streamlit as st
import pandas as pd
import urllib.parse
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Arca S&S", layout="centered")

# Links de tu planilla (Verificados)
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"
URL_RESERVAS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"
# Poné el celular de Sofía acá para el modo WhatsApp
CELULAR_ADMIN = "5491100000000" 

# --- 2. FUNCIÓN PARA CARGAR DATOS ---
def cargar_datos():
    try:
        df_s = pd.read_csv(URL_SOCIOS)
        df_r = pd.read_csv(URL_RESERVAS)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except Exception as e:
        st.error(f"Error cargando Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- 3. LÓGICA DE NAVEGACIÓN ---
st.title("🏋️ Arca S&S")
pestana = st.radio("Seleccioná tu perfil:", ["Alumno", "Administrador 🔒"], horizontal=True)
st.write("---")

df_s, df_r = cargar_datos()

# --- 4. VISTA ALUMNO ---
if pestana == "Alumno":
    if not df_s.empty:
        # Unimos nombre y apellido para el buscador
        df_s['full'] = df_s['nombre'].astype(str) + " " + df_s['apellido'].astype(str)
        lista_nombres = [""] + df_s['full'].tolist()
        
        alumno_sel = st.selectbox("Buscá tu nombre y apellido:", lista_nombres)
        
        if alumno_sel:
            fila = df_s[df_s['full'] == alumno_sel].iloc[0]
            saldo = int(fila['saldo_clases'])
            
            st.info(f"Hola **{alumno_sel}**. Clases restantes: **{saldo}**")
            
            if saldo > 0:
                col1, col2 = st.columns(2)
                with col1:
                    fec = st.date_input("Día")
                with col2:
                    hor = st.selectbox("Hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("RESERVAR TURNO", use_container_width=True):
                    # Generamos el mensaje para WhatsApp (Plan B infalible)
                    msg = f"Hola Sofi! Soy {alumno_sel}. Reservo para el {fec} a las {hor}. (Descontame una clase, me quedan {saldo-1})"
                    texto_wpp = urllib.parse.quote(msg)
                    link = f"https://wa.me/{CELULAR_ADMIN}?text={texto_wpp}"
                    
                    st.success("✅ ¡Turno confirmado!")
                    st.markdown(f'''
                        <a href="{link}" target="_blank" style="text-decoration:none;">
                            <div style="background-color:#25D366;color:white;padding:12px;text-align:center;border-radius:8px;font-weight:bold;">
                                📱 NOTIFICAR A SOFÍA POR WHATSAPP
                            </div>
                        </a>
                    ''', unsafe_allow_html=True)
            else:
                st.error("No tenés clases disponibles. Avisale a Sofía para renovar.")
    else:
        st.warning("Cargando lista de alumnos...")

# --- 5. VISTA ADMINISTRADOR ---
else:
    clave = st.text_input("Ingresá la clave de acceso:", type="password")
    if clave == "Samuel28":
        t1, t2, t3 = st.tabs(["📅 Agenda", "👥 Socios", "➕ Gestión"])
        
        with t1:
            dia_ver = st.date_input("Ver agenda del día:")
            if not df_r.empty:
                filtro = df_r[df_r['fecha'] == str(dia_ver)]
                st.dataframe(filtro[['socio_id', 'hora']], use_container_width=True, hide_index=True)
        
        with t2:
            if not df_s.empty:
                st.dataframe(df_s[['nombre', 'apellido', 'saldo_clases', 'vencimiento']], use_container_width=True, hide_index=True)
        
        with t3:
            st.subheader("Cargar Nuevo / Actualizar")
            n = st.text_input("Nombre del Alumno")
            a = st.text_input("Apellido")
            c = st.number_input("Cantidad de Clases", value=8)
            
            if st.button("GENERAR ALTA / ABONO"):
                msg_admin = f"ALTA/ABONO: {n} {a} con {c} clases."
                texto_admin = urllib.parse.quote(msg_admin)
                link_admin = f"https://wa.me/{CELULAR_ADMIN}?text={texto_admin}"
                
                st.info("Copia esto al Excel o envialo por WhatsApp:")
                st.markdown(f'<a href="{link_admin}" target="_blank">📱 ENVIAR A MI WHATSAPP</a>', unsafe_allow_html=True)
    elif clave != "":
        st.error("Clave incorrecta")
