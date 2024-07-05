import streamlit as st
import pandas as pd
from pyvis.network import Network
import pandas as pd
import networkx as nx
from login import autenticacion_usuario

def draw_graph():
    if 'df' in st.session_state and "ciclo_actual" in st.session_state and "cursos_aprobados" in st.session_state:
        df = st.session_state['df']
        ciclo_actual = int(st.session_state['ciclo_actual'])
        cursos_aprobados = st.session_state['cursos_aprobados']

        df['Ciclo'] = pd.to_numeric(df['Ciclo'], errors='coerce')
        df['Código'] = df['Código'].astype(str).str.strip()
        df['Requisito'] = df['Requisito'].astype(str).str.strip()

        df_filtrado = df[df['Ciclo'] <= ciclo_actual + 3]

        G = nx.DiGraph()
        for index, row in df_filtrado.iterrows():
            G.add_node(row['Código'], title=row['Nombre'], color='gray')
            if row['Requisito'] != 'Ninguno':
                G.add_node(row['Requisito'], title=row['Requisito'], color='gray')
                G.add_edge(row['Requisito'], row['Código'])
        for node in G:
            if node in cursos_aprobados:
                G.nodes[node]['color'] = 'green'  
            elif G.in_degree(node) == 0 or all(pred in cursos_aprobados for pred in G.predecessors(node)):
                G.nodes[node]['color'] = 'blue'  
        def mark_red(node):
            for successor in G.successors(node):
                if G.nodes[successor]['color'] not in ['green', 'blue']:
                    G.nodes[successor]['color'] = 'red'
                    mark_red(successor)  
        for node in G:
            if G.nodes[node]['color'] == 'blue':
                mark_red(node)

        nodos_mostrados = G.nodes()
        df_mostrados = df[df['Código'].isin(nodos_mostrados)].copy()
        df_mostrados = df_mostrados[['Ciclo', 'Código', 'Nombre']].drop_duplicates().sort_values(by='Ciclo')
        
        st.write("Cursos que se muestran en el grafo generado: ")
        st.dataframe(df_mostrados)

        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        for node, node_attrs in G.nodes(data=True):
            net.add_node(node, title=node, color=node_attrs['color'])
        for edge in G.edges():
            net.add_edge(edge[0], edge[1])

        net.save_graph("graph.html")
        HtmlFile = open("graph.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.components.v1.html(source_code, height=800)
    else:
        st.error("Please ensure all necessary data is loaded.")


def main():
    if autenticacion_usuario():
        st.title("Proceso de matrícula")
        if 'df' not in st.session_state:
            st.error("Primero carga el Plan de Estudios")
        else:
            if "nombre" in st.session_state and "ciclo_actual" in st.session_state and "cursos_aprobados" in st.session_state:
                st.write(f"Cursos que aprobaste: {st.session_state['cursos_aprobados']}")
                st.write(f"Ciclo actual: {st.session_state['ciclo_actual']}")
                df = st.session_state['df']
                draw_graph()
                st.sidebar.markdown("""
                ### Leyenda de Colores del Grafo de Matrícula
                - **Verde**: Cursos que ya has completado y aprobado satisfactoriamente.
                - **Gris**: Cursos en los que puedes matricularte.
                - **Azul**: Cursos en los que puedes matricularte, pues cumples con los prerequisitos
                - **Rojo**: Cursos en los que no te puedes matricular por incumplimiento de requisito.
                - Nota: La conexión con los nodos rojos representan la ruta crítica.
                """)
    else:
        st.error("Debes iniciar sesión para ver el contenido.")

if __name__ == "__main__":
    main()
