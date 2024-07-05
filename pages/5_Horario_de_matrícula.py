import streamlit as st
import pandas as pd
import random as ra
import plotly.express as px
import os
from login import autenticacion_usuario

# Configuración de página
st.set_page_config(
    page_title="Horario de Matrícula",
    page_icon="calendar",
    initial_sidebar_state="expanded",
)

# Función para generar cromosomas adaptada
class GeneradorDeCromosomas:
    def __init__(self):
        self.genes = {}

    def aula(self, curso, info_semest, ambientes, clase):
        if info_semest[curso][clase] == 'Aula':
            while True:
                ambiente = ra.choice(list(ambientes[0]))
                if ambientes[0][ambiente][0] == 'Si':
                    return ambiente
        elif info_semest[curso][clase] == 'Laboratorio':
            while True:
                ambiente = ra.choice(list(ambientes[1]))
                if ambientes[1][ambiente][0] == 'Si':
                    return ambiente
        elif info_semest[curso][clase] == 'Aula Interactiva LID':
            while True:
                ambiente = ra.choice(list(ambientes[2]))
                if ambientes[2][ambiente][0] == 'Si':
                    return ambiente
        elif info_semest[curso][clase] == 'Auditorio':
            while True:
                ambiente = ra.choice(list(ambientes[3]))
                if ambientes[3][ambiente][0] == 'Si':
                    return ambiente

    def cromosomas(self, semest, profesores_por_semestre, ambientes):
        claseT = 5
        claseP = 6
        for curso in list(semest):
            aulaTeoria = self.aula(curso, semest, ambientes, claseT)
            aulaPractica = self.aula(curso, semest, ambientes, claseP)
            docente = profesores_por_semestre.get(curso)
            self.genes[semest[curso][0]] = [docente, aulaTeoria, aulaPractica, ra.randint(1, 42), ra.randint(1, 42)]

# Función para generar la población inicial
def generar_poblacion_inicial(tamano_poblacion, cursos, profesores_por_semestre, ambientes):
    poblacion = []
    for _ in range(tamano_poblacion):
        crom = GeneradorDeCromosomas()
        crom.cromosomas(cursos, profesores_por_semestre, ambientes)
        poblacion.append(crom)
    return poblacion

# Función de fitness
def calcular_fitness(cromosoma):
    penalizacion = 0
    # Añadir lógica de penalización aquí
    return penalizacion

# Selección de mejores cromosomas
def seleccionar_mejores(valores_fitness):
    # Selección basada en el valor de fitness
    valores_fitness.sort(key=lambda x: x[1])
    return valores_fitness[:len(valores_fitness)//2]

# Obtener cromosomas seleccionados
def obtener_cromosomas_seleccionados(mejores, poblacion):
    return [poblacion[i] for i, _ in mejores]

# Crossover
def crossover(cromosomas):
    nuevos_cromosomas = []
    for i in range(0, len(cromosomas), 2):
        padre1, padre2 = cromosomas[i], cromosomas[i+1]
        hijo1_genes = {**padre1.genes, **padre2.genes}
        hijo2_genes = {**padre2.genes, **padre1.genes}
        hijo1 = GeneradorDeCromosomas()
        hijo2 = GeneradorDeCromosomas()
        hijo1.genes = hijo1_genes
        hijo2.genes = hijo2_genes
        nuevos_cromosomas.extend([hijo1, hijo2])
    return nuevos_cromosomas

# Mutación
def mutacion(cromosomas, tasa_mutacion):
    for crom in cromosomas:
        if ra.random() < tasa_mutacion:
            # Realizar mutación en los genes del cromosoma
            curso = ra.choice(list(crom.genes.keys()))
            crom.genes[curso][3] = ra.randint(1, 42)
            crom.genes[curso][4] = ra.randint(1, 42)
    return cromosomas

# Algoritmo genético
def algoritmo_genetico(tamano_poblacion, generaciones, cursos, profesores_por_semestre, ambientes):
    poblacion = generar_poblacion_inicial(tamano_poblacion, cursos, profesores_por_semestre, ambientes)

    for generacion in range(generaciones):
        # Calcular el fitness
        valores_fitness = [(i, calcular_fitness(crom)) for i, crom in enumerate(poblacion)]

        # Seleccionar los mejores
        mejores = seleccionar_mejores(valores_fitness)

        # Convertirlos a diccionarios
        cromosomas_seleccionados = obtener_cromosomas_seleccionados(mejores, poblacion)

        # Aplicar crossover
        nuevos_cromosomas_crossover = crossover(cromosomas_seleccionados)

        # Aplicar mutación
        poblacion = mutacion(nuevos_cromosomas_crossover, 0.01)

    return poblacion

# Función para preparar datos para el gráfico
def preparar_datos(df, periodos_df):
    dias_a_fechas = {
        "Lunes": "2024-01-02",
        "Martes": "2024-01-03",
        "Miércoles": "2024-01-04",
        "Jueves": "2024-01-05",
        "Viernes": "2024-01-06",
        "Sábado": "2024-01-07",
        "Domingo": "2024-01-08"
    }

    eventos = []

    for _, fila in df.iterrows():
        curso = fila['Curso']
        docente = fila['Docente']
        aula_teoria = fila['Aula de Teoría']
        aula_practica = fila['Aula de Práctica']
        hora_teoria = fila['Hora de Teoría']
        hora_practica = fila['Hora de Práctica']

        dia_teoria, tiempo_teoria = hora_teoria.split(": ")
        inicio_teoria, fin_teoria = tiempo_teoria.split(" - ")
        dia_practica, tiempo_practica = hora_practica.split(": ")
        inicio_practica, fin_practica = tiempo_practica.split(" - ")

        eventos.append({
            'Curso': curso,
            'Docente': docente,
            'Aula': aula_teoria,
            'Inicio': f"{dias_a_fechas[dia_teoria]} {inicio_teoria}:00",
            'Fin': f"{dias_a_fechas[dia_teoria]} {fin_teoria}:00",
            'Tipo': 'Teoría'
        })

        eventos.append({
            'Curso': curso,
            'Docente': docente,
            'Aula': aula_practica,
            'Inicio': f"{dias_a_fechas[dia_practica]} {inicio_practica}:00",
            'Fin': f"{dias_a_fechas[dia_practica]} {fin_practica}:00",
            'Tipo': 'Práctica'
        })

    return pd.DataFrame(eventos)

# Función para visualizar el horario
def visualizar_horario(df, periodos_df):
    df_eventos = preparar_datos(df, periodos_df)

    colores_curso = px.colors.qualitative.Light24[:df_eventos["Curso"].nunique()]
    color_map = {curso: colores_curso[i % len(colores_curso)] for i, curso in enumerate(df_eventos["Curso"].unique())}

    fig = px.timeline(
        df_eventos,
        x_start="Inicio",
        x_end="Fin",
        y="Curso",
        color="Curso",
        color_discrete_map=color_map,
        title="Horario",
        hover_data=["Docente", "Aula"],
        labels={"Inicio": "Hora de Inicio", "Fin": "Hora de Fin"}
    )

    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(
        xaxis_title="Hora",
        yaxis_title="Curso",
        xaxis=dict(
            tickformat="%a %H:%M"
        ),
        title_x=0.5
    )

    st.plotly_chart(fig)

def main():
    if autenticacion_usuario():
        st.title("Horario de Matrícula")

        # Verificar si el plan de estudios está cargado en la sesión
        if 'df' not in st.session_state:
            st.error("Primero carga el Plan de Estudios en la página 'Subir Plan de Estudios'")
            return
        
        # Cargar los datos necesarios
        try:
            df_cursos = st.session_state['df']

            file_path_salones = os.path.join(os.path.dirname(__file__), 'ModelarSalones.xlsx')
            df_salones = pd.read_excel(file_path_salones)
            file_path_profesores = os.path.join(os.path.dirname(__file__), 'asignaturas_con_profesores.xlsx')
            df_profesores = pd.read_excel(file_path_profesores)
            file_path_periodos = os.path.join(os.path.dirname(__file__), 'Asignaciones.xlsx')
            df_periodos = pd.read_excel(file_path_periodos, sheet_name="Periodo")
        except Exception as e:
            st.error(f"Error al cargar los archivos: {e}")
            return
        # Procesar datos de salones
        aulas = df_salones[df_salones['Tipo'] == 'Aula'].set_index('Aulas').to_dict('index')
        laboratorios = df_salones[df_salones['Tipo'] == 'Laboratorio'].set_index('Aulas').to_dict('index')
        aulas_interactivas = df_salones[df_salones['Tipo'] == 'Aula Interactiva LID'].set_index('Aulas').to_dict('index')
        auditorios = df_salones[df_salones['Tipo'] == 'Auditorio'].set_index('Aulas').to_dict('index')
        ambientes = [aulas, laboratorios, aulas_interactivas, auditorios]
        
        # Procesar datos de profesores
        profesores_por_semestre_CodNom = df_profesores.set_index('Código')['Profesor'].to_dict()

        if "nombre" in st.session_state and "ciclo_actual" in st.session_state and "cursos_aprobados" in st.session_state:
            st.write(f"Ciclo actual: {st.session_state['ciclo_actual']}")

            ciclo_actual = st.session_state['ciclo_actual']
            
            # Filtrar los cursos del ciclo actual
            cursos_ciclo_actual = df_cursos[df_cursos['Ciclo'] == ciclo_actual]

            # Ejecutar el algoritmo genético
            tamano_poblacion = 100
            generaciones = 10
            poblacion_final = algoritmo_genetico(tamano_poblacion, generaciones, cursos_ciclo_actual.set_index('Código').T.to_dict('list'), profesores_por_semestre_CodNom, ambientes)

            # Seleccionar el mejor cromosoma (el primero de la lista final de población)
            mejor_cromosoma = poblacion_final[0]

            # Convertir los genes a un DataFrame
            df_cromosoma = pd.DataFrame(mejor_cromosoma.genes).T.reset_index()
            df_cromosoma.columns = ['Curso', 'Docente', 'Aula de Teoría', 'Aula de Práctica', 'Hora de Teoría', 'Hora de Práctica']

            # Ajustar los datos de las horas
            for id, filas in df_cromosoma.iterrows():
                id_periodo1 = filas['Hora de Teoría']
                filaHoraT = df_periodos.loc[df_periodos['ID'] == id_periodo1].squeeze()
                hora_de_inicio = filaHoraT['Hora_Inicio']
                dia = filaHoraT['Día']
                df_cromosoma.at[id, 'Hora de Teoría'] = f'{dia}: {hora_de_inicio} - {hora_de_inicio + 2}'

                id_periodo2 = filas['Hora de Práctica']
                filaHoraT = df_periodos.loc[df_periodos['ID'] == id_periodo2].squeeze()
                hora_de_inicio = filaHoraT['Hora_Inicio']
                dia = filaHoraT['Día']
                df_cromosoma.at[id, 'Hora de Práctica'] = f'{dia}: {hora_de_inicio} - {hora_de_inicio + 2}'

            # Mostrar lista de cursos que llevará el estudiante en el ciclo actual en la sidebar
            st.sidebar.markdown("### Cursos que llevarás en el ciclo actual:")
            for index, row in df_cromosoma.iterrows():
                st.sidebar.write(f"- **{row['Curso']}**: {row['Docente']} ({row['Hora de Teoría']}, {row['Hora de Práctica']})")

            # Visualizar el horario óptimo
            visualizar_horario(df_cromosoma, df_periodos)


    else:
        st.error("Debes iniciar sesión para ver el contenido.")

if __name__ == "__main__":
    main()
