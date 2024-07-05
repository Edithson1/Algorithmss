import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from login import autenticacion_usuario

st.set_page_config(
    page_title="Portal de Matrícula",
    page_icon="school",
    initial_sidebar_state="expanded",
)

#page_bg_img = """
#    <style>
#    [data-testid="stAppViewContainer"] > .main {
#        background-image: url("https://img.freepik.com/foto-gratis/fondo-acuarela-pintada-mano-forma-cielo-nubes_24972-1095.jpg");
#        background-size: cover;
#        background-position: center;
#        background-attachment: fixed;
#    }
#    </style>
#"""
#st.markdown(page_bg_img, unsafe_allow_html=True)

# Función que permite arreglar los nombres de los cursos
def arreglarNombres(df, columna):
    nombresCorregidos = []
    for palabras in df[columna]:
        listaPalabras = palabras.split(' ')
        palabras_actualizadas = []
        for palabra in listaPalabras:
            if len(palabra) > 4:
                letra = palabra[0].upper()
                palabra_actualizada = letra + palabra[1:]
            else:
                palabra_actualizada = palabra
            palabras_actualizadas.append(palabra_actualizada)
        nombresCorregidos.append(' '.join(palabras_actualizadas)) 
    return nombresCorregidos


# Función que nos permmite obtener los acrónimos de cada curso
def obtenerAcronimo(df, nombresCorregidos):
  listaAcronimos = []
  for palabras in df['Nombre']:
    listaPalabras = palabras.split()
    ultimaPal = listaPalabras[-1]
    palabras_actualizadas = []
    letTem = ''
    for palabra in listaPalabras:
        if len(palabra) > 4:
            letra = palabra[0].upper()
            palabra_actualizada = letra + palabra[1:]
            letTem += letra
        else:
            palabra_actualizada = palabra
        palabras_actualizadas.append(palabra_actualizada)
    nombresCorregidos.append(' '.join(palabras_actualizadas))
    if len(ultimaPal) < 4:
        letTem += ultimaPal 
    if letTem in listaAcronimos:
        letTem += letTem[-1]
        listaAcronimos.append(letTem)
        continue
    listaAcronimos.append(letTem)
  
  return listaAcronimos


# Función que me permite generara los nodos en base a nuestro DatFrame
def generarDatosNodos(df, acronimos):
    asigCodAcro = {}
    asigAcroCod = {}
    nombresNivel = {}
    cursosNivel = {}
    posic = {}
    nombresCiclo = []

    ##
    nombreCredito = {}
    credNivel = {}
    listas = []
    asigCredNivel = []
    tep = set()
    listAristas = []
    listAris= []
    ##


    for index, row in df.iterrows():
        asigCodAcro[row['Código']] = row['Acrónimo']
    for index, row in df.iterrows():
        asigAcroCod[row['Acrónimo']] = row['Código']
    nivel = ["PRIMER CICLO","SEGUNDO CICLO","TERCER CICLO","CUARTO CICLO",
                "QUINTO CICLO","SEXTO CICLO","SÉTIMO CICLO","OCTAVO CICLO","NOVENO CICLO","DÉCIMO CICLO"]

    for num, nombre in enumerate(nivel):
        nombresNivel[nivel[num]] = num+1

    for nombre, ciclo in nombresNivel.items():
        dicTem = []
        for index, row in df.iterrows():
            if ciclo == row['Ciclo']:
                dicTem.append(row['Acrónimo'])
        cursosNivel[nombre] = dicTem
    ##
    for cred, nivel in nombresNivel.items():
        credNivel[nivel] = cred

    for index, row in df.iterrows():
        codigo = row['Requisito']

        if codigo not in asigCodAcro and codigo not in nombreCredito:
            if '/' not in codigo:
                nombreCredito[row['Requisito']] = row['Ciclo'] - 1
            else:
                partes = codigo.split('/')
                partes = [parte.strip() for parte in partes]
                for i in partes:
                    nombreCredito[i] = row['Ciclo'] - 1
                    if i in df['Código'].values:
                        tep.add(i)
                        listas.append((i,row['Código']))

    for nombreCred, ciclo in nombreCredito.items():
        if ciclo in credNivel:
            nom = credNivel[ciclo]
            asigCredNivel.append({nom:nombreCred})
    for index, row in df.iterrows():
        for i in asigCredNivel:
            for j,k in i.items():
                if k not in tep:
                    cursosNivel[j].append(k)
                    tep.add(k)
    ##

    for contador, (i, j) in enumerate(cursosNivel.items()):
        c = 1
        nombresCiclo.append(i)
        if contador % 2==0:
            c += 0.5
        for k in j:
            posic[k] = (c, 20 - contador*2)
            c +=1
    ##
    for index, row in df.iterrows():
        acronimo = asigAcroCod[row['Acrónimo']]
        requisito = row['Requisito']
        if requisito != 'Ninguno':
            arist = (requisito,acronimo)
            listAristas.append(arist)
    for i in listAristas:
        if '/'not in i[0]:
            listas.append(i)

    for tupla in listas:
        if tupla[0] in asigCodAcro:
            updated_i = (asigCodAcro[tupla[0]], asigCodAcro[tupla[1]])
            listAris.append(updated_i)
        else:
            listAris.append((tupla[0], asigCodAcro[tupla[1]]))
    for i in listAris:
        if i[0] not in acronimos:
            acronimos.append(i[0])
    ##

    return asigCodAcro,asigAcroCod,listAris,acronimos,cursosNivel,posic,nombresCiclo


# Función que nos permite mostrar la malla curricular como gráfo
def mostrarGrafo(acronimos,posic,listAris):
    G = nx.DiGraph()
    G.add_nodes_from(acronimos)
    G.add_edges_from(listAris)
    plt.figure(figsize=(17, 27))
    nx.draw(G, posic, with_labels=True, node_color='skyblue', node_size=8000, edge_color='black', linewidths=1, font_size=20)
    
  
def main():
    if autenticacion_usuario():
        st.title("Plan de estudios")
        if 'df' not in st.session_state:
            st.error("Primero carga el Plan de Estudios")
        else:
            df = st.session_state['df']
            nombresCorregidos = arreglarNombres(df, 'Nombre')
            df['Nombre'] = nombresCorregidos
            nombresCorregidos = arreglarNombres(df, 'Nombre Requisito')
            df['Nombre Requisito'] = nombresCorregidos
            acronimos = obtenerAcronimo(df,nombresCorregidos)
            df['Acrónimo'] = acronimos
            asigCodAcro,asigAcroCod,listAris,acronimos1,cursosNivel,posic,nombresCiclo = generarDatosNodos(df,acronimos)
            mostrarGrafo(acronimos1,posic,listAris)
            
            posicionNivel = {}
            for nivel, nodos in cursosNivel.items():
                y_pos = sum([posic[node][1] for node in nodos]) / len(nodos) 
                posicionNivel[nivel] = (0.5, y_pos)

            for nivel, posicion in posicionNivel.items():
                plt.text(posicion[0], posicion[1], nivel, rotation=90, fontsize=20, verticalalignment='center', horizontalalignment='center')
            nivelPresionado = st.sidebar.selectbox("Selecciona el nivel", nombresCiclo)
            if nivelPresionado:
                st.sidebar.markdown(f"**Información sobre el {nivelPresionado}:**")
                if nivelPresionado in cursosNivel:
                    cursos = cursosNivel[nivelPresionado]
                    for curso in cursos:
                        
                        curso_nombre = {}
                        tipo_nombre = {}
                        sede_nombre = {}
                        modalidad_nombre = {}
                        cred_nombre = {}
                        req_nombre = {}

                        for index, row in df.iterrows():
                            curso_nombre[row['Acrónimo']] = row['Nombre']
                            tipo_nombre[row['Acrónimo']] = row['Tipo']
                            sede_nombre[row['Acrónimo']] = row['Sede']
                            modalidad_nombre[row['Acrónimo']] = row['Modalidad']
                            cred_nombre[row['Acrónimo']] = row['Créditos']
                            req_nombre[row['Acrónimo']] = row['Nombre Requisito']
                        if curso in curso_nombre:
                            st.sidebar.write(f"**{curso}: {curso_nombre[curso]}**")
                            st.sidebar.write(f"- Tipo: *{tipo_nombre[curso]}*")
                            st.sidebar.write(f"- Sede: *{sede_nombre[curso]}*")
                            st.sidebar.write(f"- Modalidad: *{modalidad_nombre[curso]}*")
                            st.sidebar.write(f"- N° Céditos: *{cred_nombre[curso]}*")
                            st.sidebar.write(f"- Requisito: *{req_nombre[curso]}*")
                            
                else:
                    st.sidebar.write("Información específica no disponible para este ciclo.")
            st.pyplot(plt)
    else:
        st.error("Debes iniciar sesión para ver el contenido.")

if __name__ == "__main__":
    main()
