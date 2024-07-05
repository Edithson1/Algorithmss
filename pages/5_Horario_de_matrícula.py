import streamlit as st
import pandas as pd
import random as ra
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
    conjunto_de_cromosomas = {}
    for i in range(tamano_poblacion):
        cromosoma = GeneradorDeCromosomas()
        cromosoma.cromosomas(cursos, profesores_por_semestre, ambientes)
        conjunto_de_cromosomas[i] = cromosoma.genes
    return conjunto_de_cromosomas

# Función de fitness
def calcular_fitness(conjunto_de_cromosomas):
    def determinar_dia(periodo):
        if 0 <= periodo <= 7:
            return 'Lunes'
        elif 8 <= periodo <= 14:
            return 'Martes'
        elif 15 <= periodo <= 21:
            return 'Miércoles'
        elif 22 <= periodo <= 28:
            return 'Jueves'
        elif 29 <= periodo <= 35:
            return 'Viernes'
        elif 36 <= periodo <= 42:
            return 'Sábado'
        else:
            return 'Desconocido'

    penalizaciones = {
        1: -15,
        2: -5,
        3: 0,
        4: -50,
        5: -1000,
        6: -1000
    }

    def calcular_penalizacion_solapamientos(cromosoma):
        periodos = []
        for curso, datos in cromosoma.items():
            periodos.extend(datos[-2:])
        if len(periodos) != len(set(periodos)):
            return -1000
        return 0

    def calcular_penalizacion_cantidad_de_clases(cromosoma):
        contador_dias = {
            'Lunes': 0,
            'Martes': 0,
            'Miércoles': 0,
            'Jueves': 0,
            'Viernes': 0,
            'Sábado': 0
        }
        for curso, datos in cromosoma.items():
            periodos = datos[-2:]
            for periodo in periodos:
                dia = determinar_dia(periodo)
                if dia in contador_dias:
                    contador_dias[dia] += 1
        total_penalizacion_cantidad_de_clases = 0
        for dia, cuenta in contador_dias.items():
            if cuenta in penalizaciones:
                total_penalizacion_cantidad_de_clases += penalizaciones[cuenta]
        return total_penalizacion_cantidad_de_clases

    def calcular_penalizacion_huecos(cromosoma):
        periodos_por_dia = {
            'Lunes': [],
            'Martes': [],
            'Miércoles': [],
            'Jueves': [],
            'Viernes': [],
            'Sábado': []
        }
        for curso, datos in cromosoma.items():
            periodos = datos[-2:]
            for periodo in periodos:
                dia = determinar_dia(periodo)
                periodos_por_dia[dia].append(periodo)
        penalizacion_total_huecos = 0
        for dia, periodos in periodos_por_dia.items():
            periodos.sort()
            a = 0
            penalizacion_huecos = 0
            penalizacion_extensiones = 0
            for i in range(len(periodos) - 1):
                gap_size = periodos[i + 1] - periodos[i] - 1
                if gap_size > 0:
                    penalizacion_huecos += (-15 * a) - 15
                    penalizacion_extensiones += -10 * gap_size
                    a += 1
            penalizacion_total_huecos += penalizacion_huecos + penalizacion_extensiones
        return penalizacion_total_huecos

    valores_fitness = {}
    for cromosoma_id, cromosoma in conjunto_de_cromosomas.items():
        penalizacion_solapamientos = calcular_penalizacion_solapamientos(cromosoma)
        penalizacion_cantidad_clases = calcular_penalizacion_cantidad_de_clases(cromosoma)
        penalizacion_huecos = calcular_penalizacion_huecos(cromosoma)

        valor_fitness = penalizacion_solapamientos + penalizacion_cantidad_clases + penalizacion_huecos
        valores_fitness[cromosoma_id] = valor_fitness

    return valores_fitness

# Selección de mejores cromosomas
def seleccionar_mejores(valores_fitness):
    valores_fitness_ordenados = dict(sorted(valores_fitness.items(), key=lambda item: item[1], reverse=True))
    mitad = max(len(valores_fitness_ordenados) // 2, 2)  # Asegúrese de que al menos dos cromosomas sean seleccionados
    mitad_diccionario = dict(list(valores_fitness_ordenados.items())[:mitad])
    return mitad_diccionario

# Obtener cromosomas seleccionados
def obtener_cromosomas_seleccionados(mitad_diccionario, conjunto_de_cromosomas):
    cromosomas_seleccionados = {}
    for cromosoma_id in mitad_diccionario.keys():
        cromosomas_seleccionados[cromosoma_id] = conjunto_de_cromosomas[cromosoma_id]
    return cromosomas_seleccionados

# Crossover
def crossover(cromosomas_seleccionados):
    nuevos_cromosomas = {}
    ids = list(cromosomas_seleccionados.keys())
    for i in range(0, len(ids), 2):
        if i+1 < len(ids):
            padre1, padre2 = cromosomas_seleccionados[ids[i]], cromosomas_seleccionados[ids[i+1]]
            hijo1_genes = {**padre1, **padre2}
            hijo2_genes = {**padre2, **padre1}
            nuevos_cromosomas[ids[i]] = hijo1_genes
            nuevos_cromosomas[ids[i+1]] = hijo2_genes
    return nuevos_cromosomas

# Mutación
def mutacion(cromosomas, tasa_mutacion):
    for crom in cromosomas.values():
        if ra.random() < tasa_mutacion:
            curso = ra.choice(list(crom.keys()))
            crom[curso][3] = ra.randint(1, 42)
            crom[curso][4] = ra.randint(1, 42)
    return cromosomas

# Algoritmo genético
def algoritmo_genetico(tamano_poblacion, generaciones, cursos, profesores_por_semestre, ambientes):
    poblacion = generar_poblacion_inicial(tamano_poblacion, cursos, profesores_por_semestre, ambientes)

    for generacion in range(generaciones):
        # Calcular el fitness
        valores_fitness = calcular_fitness(poblacion)

        # Seleccionar los mejores
        mejores = seleccionar_mejores(valores_fitness)

        # Obtener cromosomas seleccionados
        cromosomas_seleccionados = obtener_cromosomas_seleccionados(mejores, poblacion)

        # Verificar que el número de cromosomas seleccionados sea par
        if len(cromosomas_seleccionados) < 2:
            raise ValueError("Número de cromosomas seleccionados es menor que 2. Asegúrese de que la población inicial sea suficiente.")
        if len(cromosomas_seleccionados) % 2 != 0:
            cromosomas_seleccionados[list(cromosomas_seleccionados.keys())[0]] = cromosomas_seleccionados[list(cromosomas_seleccionados.keys())[1]]

        # Aplicar crossover
        nuevos_cromosomas_crossover = crossover(cromosomas_seleccionados)

        # Aplicar mutación
        poblacion = mutacion(nuevos_cromosomas_crossover, 0.01)
    return poblacion

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
            mejor_cromosoma = list(poblacion_final.values())[0]

            # Convertir los genes a un DataFrame
            df_cromosoma = pd.DataFrame(mejor_cromosoma).T.reset_index()
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

            # Mostrar el horario detallado en la pestaña principal
            st.write("### Horario del Ciclo Actual")
            st.write("Este es el horario generado para tus cursos del ciclo actual:")

            horario_detallado = []

            for _, row in df_cromosoma.iterrows():
                curso = row['Curso']
                docente = row['Docente']
                nombre_curso = df_cursos.loc[df_cursos['Código'] == curso, 'Nombre'].values
                if len(nombre_curso) > 0:
                    nombre_curso = nombre_curso[0]
                else:
                    nombre_curso = "Nombre de curso no encontrado"
                hora_teoria = row['Hora de Teoría']
                hora_practica = row['Hora de Práctica']
                aula_teoria = row['Aula de Teoría']
                aula_practica = row['Aula de Práctica']

                horario_detallado.append({
                    'Código del Curso': curso,
                    'Nombre del Curso': nombre_curso,
                    'Docente': docente,
                    'Hora de Teoría': hora_teoria,
                    'Aula de Teoría': aula_teoria,
                    'Hora de Práctica': hora_practica,
                    'Aula de Práctica': aula_practica
                })

            df_horario = pd.DataFrame(horario_detallado)
            st.dataframe(df_horario)
    else:
        st.error("Debes iniciar sesión para ver el contenido.")

if __name__ == "__main__":
    main()
