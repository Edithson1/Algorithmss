import streamlit as st
import pandas as pd

from login import autenticacion_usuario

# Función que permite verificar que los nombres de las columnas, como parámetro, estén en el DataFrame
def verificarDataFrame(df):
    nombresColumnas = ['Ciclo', 'Código', 'Nombre', 'Requisito', 'Nombre Requisito', 'Tipo', 'Sede', 'Modalidad', 'Créditos']
    for columna in nombresColumnas:
        if columna not in df.columns:
            raise ValueError(f"El DataFrame no tiene la columna requerida: {columna}")
    return df


# Función que permite la lectura de DataFrame
def leerDataFrame(upload_file):
    filename = upload_file.name  
    extension = filename.split('.')[-1]  
    if extension == 'csv':
        data = pd.read_csv(upload_file)
    elif extension == 'xlsx':
        data = pd.read_excel(upload_file)
    else:
        raise ValueError("¡Este tipo de archivo no es admitido!")

    verificarDataFrame(data)

    return data


def main():
    if autenticacion_usuario():
        st.title("Plan de estudios")
        upload_file = st.file_uploader('Subir el plan de estudios correspondiente a tu carrera')
        st.write("IMPORTANTE: Considere que el archivo debe contener las siguientes columnas.")
        st.write('Ciclo, Código, Nombre, Requisito, Nombre Requisito, Tipo ,Sede, Modalidad, Créditos')
        if upload_file is not None:
            filename = upload_file.name  # Obtener el nombre del archivo
            st.write(f"Archivo cargado: {filename}")  # Mostrar el nombre del archivo
            try:
                df = leerDataFrame(upload_file)
                st.session_state['df'] = df
                st.write("¡Archivo cargado y verificado correctamente!")
                st.write("(●'◡'●)")
            except ValueError as error:
                st.error(f"Error al cargar el archivo: {error}")
    else:
        st.error("Debes iniciar sesión para ver el contenido.")


if __name__ == "__main__":
    main()
