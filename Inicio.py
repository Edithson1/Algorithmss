import streamlit as st
import pandas as pd
import os

# Base de datos de alumno
file_path = os.path.join(os.path.dirname(__file__), 'bd_alumnos.csv')
df_alumnos = pd.read_csv(file_path)

# Sistema de Login
def entrada_credencial():
    user_input = st.session_state.get("user", "").strip()
    passwd_input = st.session_state.get("passwd", "").strip()

    # Validate credentials
    if any((df_alumnos['userid'] == user_input) & (df_alumnos['password'] == passwd_input)):
        st.session_state["autenticacion"] = True

        # Extracción de columnas por usuario para luego trabajar con ellas
        fila_de_usuarios = df_alumnos[df_alumnos['userid'] == user_input].iloc[0]
        st.session_state['nombre'] = fila_de_usuarios['nombre']
        st.session_state['ciclo_actual'] = fila_de_usuarios['ciclo_actual']
        st.session_state['cursos_aprobados'] = fila_de_usuarios['cursos_aprobados']
    else:
        st.session_state["autenticacion"] = False
        st.error("Contraseña/Usuario inválido")

def autenticacion_usuario():
    if "autenticacion" in st.session_state and st.session_state["autenticacion"]:
        # Logout option in the sidebar
        if st.sidebar.button("Cerrar Sesión"):
            # Resetting session state to initial state
            for key in ["autenticacion", "user", "passwd", "validar"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()  # Rerun the app to reflect the reset state
        return True

    st.markdown("<h1 style='text-align: center;'>Iniciar Sesión 👋</h1>", unsafe_allow_html=True)
    st.text_input(label="Usuario:", value="", key="user", on_change=entrada_credencial)
    st.text_input(label="Contraseña:", value="", key="passwd", type="password", on_change=entrada_credencial)

    if st.button("Iniciar Sesión"):
        entrada_credencial()  # Check credentials directly when the button is clicked

    return st.session_state.get("autenticacion", False)

