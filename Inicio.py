import streamlit as st
import pandas as pd
import os
from login import autenticacion_usuario
import json

######Esta es la pagina principal(MAIN)##########

####Configuracion de página#######
st.set_page_config(
    page_title="Portal de Matrícula",
    page_icon="school",
    initial_sidebar_state="expanded",
)
##################################

# Base de datos de alumno
file_path = os.path.join(os.path.dirname(__file__), 'bd_alumnos.csv')
df_alumnos = pd.read_csv(file_path)
########################

def main():
    if autenticacion_usuario():
        st.title("Datos del estudiante")
        if "nombre" in st.session_state and "ciclo_actual" in st.session_state and "cursos_aprobados" in st.session_state :
        # Display a greeting with the user's name
            st.write(f"Hola, {st.session_state['nombre']}!")

            st.write(f"Ciclo actual: {st.session_state['ciclo_actual']}")

if __name__ == "__main__":
    main()


