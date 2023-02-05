# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 19:01:33 2023

@author: cgarcia
"""

import streamlit as st # streamlit es una libreria de Python para crear aplicaciones de dashboards interactivos y rápidos
import pandas as pd # pandas es una libreria de análisis de datos en Python
import csv # libreria para lectura de archivos CSV
import matplotlib.pyplot as plt # libreria de visualización de datos en Python
from wordcloud import WordCloud # libreria para crear nubes de palabras
import plotly.express as px # libreria para crear visualizaciones interactivas en Python
from nltk.corpus import stopwords # libreria para procesamiento de lenguaje natural
import base64 # libreria para codificación/decodificación en base64


# Función para leer una imagen y devolverlo en formato base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#Lectura de la imagen como base64
img = get_img_as_base64("man-g5075a18e1_1920.jpg")

#Establecimiento del estilo de fondo para la aplicación
page_bg_img = f"""

<style>
[data-testid="stAppViewContainer"] > .main {{
background-color: #fafaee;
opacity: 1;
background-image: radial-gradient(#e1e1d7 0.5px, #fafaee 0.5px);
background-size: 10px 10px;
}}
[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img}");
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""
#Aplicación del estilo en formato markdown
st.markdown(page_bg_img, unsafe_allow_html = True)

#Lectura de los datos de las obras
df = pd.read_csv('artworks.csv', delimiter = ',')

#Establecimiento del título de la aplicación
st.title('Colección Escuela Italiana')
st.title('_:blue[Museo del Prado]_')

#Diccionario con las páginas disponibles en la aplicación
PAGE_DICT = {
    "Ficha técnica": "fichatec.py",
    "Línea del tiempo": "timeline.py"
}


#La función FichaTecnica muestra información detallada de un cuadro seleccionado por el usuario a través de una lista desplegable
def FichaTecnica():

    titulo_cuadro = st.selectbox("_Seleccione un cuadro_", df["title"])

    selected_row = df[df["title"] == titulo_cuadro]

    st.write("**Título**: ", selected_row["title"].values[0])
    st.write("**Autor**: ", selected_row["author"].values[0])
    st.write("**Técnica**: ", selected_row["technical"].values[0])
    st.write("**Soporte o Material**: ", selected_row["support_material"].values[0])
    st.write("**Año**: ", selected_row["date"].values[0])

    st.image(selected_row["image"].values[0], width=250)

#La función LineaTiempo muestra una línea del tiempo con las obras agrupadas por año y el usuario puede seleccionar un año para ver los cuadros de ese período
def LineaTiempo():
   
    data = []
    with open("artworks.csv", "r", encoding="utf-8") as f:
         reader = csv.DictReader(f)
         for row in reader:
             data.append(row)

    siglos = {}
    for obra in data:
         siglo = int(obra['date']) // 100 * 100
         if siglo not in siglos:
             siglos[siglo] = []
         siglos[siglo].append(obra)
         
    selected_century = st.sidebar.radio("Seleccione el año:", list(siglos.keys()))

    st.write("**Línea del tiempo agrupada por años**:")
    st.write(f"Año {selected_century}:")
    for obra in siglos[selected_century]:
         title = obra['title']
         st.write(f"- {title} ({obra['date']})")
         st.image(obra['image'], width=150)
 
#La función show_page muestra la página seleccionada en el sidebar
def show_page(page_name):
    """Mostrar la página seleccionada en el sidebar."""
    if page_name == "Ficha técnica":
        FichaTecnica()
    elif page_name == "Línea del tiempo":
        LineaTiempo()

#La función main es la función principal que muestra el menú de navegación en el sidebar y llama a la función show_page para mostrar la página seleccionada
def main():
    """Función principal que muestra el menú de navegación en el sidebar."""
    st.sidebar.title("Colección Escuela Italiana")
    selected_page = st.sidebar.selectbox("_**Escoja una sección**_", list(PAGE_DICT.keys()))
    show_page(selected_page)

if __name__ == "__main__":
    main()
    
#Desactivamos la advertencia de depreciación en caso de que se use una versión antigua de Matplotlib con Streamlit
st.set_option('deprecation.showPyplotGlobalUse', False)

# Función para mostrar el set de datos
def show_dataset():
    data = df[(df["date"] >= 1345) & (df["date"] <= 1948)]
    st.write(data)
    if st.button("Descargar set de datos"):
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # encoding the csv file
        href = f'<a href="data:file/csv;base64,{b64}" download="artworks.csv">Pulsa aquí para descargar</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("¡El archivo ha sido descargado exitosamente!", icon="🎨")


# Función para mostrar el histograma
def show_histogram():
    
    start_year = st.sidebar.slider("Selecciona el año de inicio", int(df["date"].min()), int(df["date"].max()), int(df["date"].min()))
    end_year = st.sidebar.slider("Selecciona el año final", int(df["date"].min()), int(df["date"].max()), int(df["date"].max()))

    year_creation = df[(df["date"] >= start_year) & (df["date"] <= end_year)]["date"]
    fig = px.histogram(year_creation, nbins=30)
    fig.update_layout(xaxis_title="Año de creación", yaxis_title="Número de obras")
    st.plotly_chart(fig)
    
# Función para mostrar el gráfico de barras agrupado por técnica y material
def show_grouped_bar_chart():
    df["support_material_grouped"] = df["support_material"].copy()
    df.loc[df["support_material"].str.contains("tabla"), "support_material_grouped"] = "tabla"
    df.loc[df["support_material"].str.contains("lienzo"), "support_material_grouped"] = "lienzo"
    df.loc[df["support_material"].str.contains("lamina"), "support_material_grouped"] = "lamina"
    df.loc[df["support_material"].str.contains("pizarra"), "support_material_grouped"] = "pizarra"
    df.loc[df["support_material"].str.contains("papel"), "support_material_grouped"] = "papel"
    df.loc[df["support_material"].str.contains("cartulina"), "support_material_grouped"] = "cartulina"
    df.loc[df["support_material"].str.contains("carton"), "support_material_grouped"] = "carton"
    
    grouped = df.groupby(["technical", "support_material_grouped"]).size().reset_index(name="count")
    fig = px.bar(grouped, x='technical', y='count', color='support_material_grouped')
    fig.update_layout(xaxis_title="Técnica", yaxis_title="Número de obras")
    st.plotly_chart(fig)


# Función para mostrar el gráfico de dispersión
def show_scatter_plot():
    fig = px.scatter(df, x="technical", y="support_material")
    fig.update_layout(xaxis_title="Técnica", yaxis_title="Material")
    st.plotly_chart(fig)


# Función para mostrar el mapa de calor
def show_heatmap():
    pivot = df.pivot_table(index="technical", columns="support_material", values="title", aggfunc="count")
    fig = px.imshow(pivot, color_continuous_scale="rdylbu")
    fig.update_layout(xaxis_title="Soporte o Material", yaxis_title="Técnica")
    fig.update_coloraxes(cmin=0, cmax=50)
    st.plotly_chart(fig)

# Función para mostrar el gráfico de nube de palabras
import nltk
nltk.download('stopwords')
stopwords = set(stopwords.words("spanish"))
stopwords.update(["de", "la", "el", "en", "y", "a", "los", "del", "que", "con"])

def show_wordcloud():
    title_text = " ".join(df["title"])
    wordcloud = WordCloud(width=800, height=800, background_color="white", stopwords=stopwords).generate(title_text)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    st.pyplot()

# Popularidad de la técnica

def show_technique_popularity():
    techniques = df['technical'].value_counts().reset_index()
    techniques.columns = ['technical', 'count']
    fig = px.pie(techniques, values='count', names='technical')
    st.plotly_chart(fig)
    
# Autores populares

def show_popular_authors():
    authors = df['author'].value_counts().reset_index()
    authors.columns = ['author', 'count']
    fig = px.bar(authors, x='author', y='count')
    st.plotly_chart(fig)

#Evolución de la técnica

def show_plot_technique_evolution():
    df['year'] = df['date']
    fig = px.line(df, x='year', y='technical', color='technical',
                  line_group='technical', hover_name='technical')
    st.plotly_chart(fig)

# Relación entre la popularidad del autor y la técnica

def show_plot_author_technique_relation():
     df['author_popularity'] = df.groupby('author')['technical'].transform('count')
     df['num_artworks_technique'] = df.groupby(['author', 'technical'])['technical'].transform('count')
     fig = px.scatter(df, x='author_popularity', y='num_artworks_technique',
                      color='technical', hover_name='technical')
     st.plotly_chart(fig)

# Relación entre la popularidad del autor y el soporte o material
def show_plot_author_material_relation():
    df['author_popularity'] = df.groupby('author')['support_material'].transform('count')
    df['num_artworks_material'] = df.groupby(['author', 'support_material'])['support_material'].transform('count')
    fig = px.scatter(df, x='author_popularity', y='num_artworks_material',
                     color='support_material', hover_name='support_material')
    st.plotly_chart(fig)

st.title("Explorador de obras de arte")
st.markdown("Selecciona una de las opciones de la barra lateral")
st.sidebar.title("Explorador de obras de arte")
st.sidebar.title("_Opciones_")
if st.sidebar.checkbox("**Set de datos**"):
    st.markdown("**Muestra el set de datos originados de la web del Museo del Prado**")
    show_dataset()
if st.sidebar.checkbox("**Distribución de años de las obras de arte**"):
    st.markdown("**Muestra el histograma de la distribución de años de creación de las obras de arte**")
    show_histogram()    
if st.sidebar.checkbox("**Relación entre la técnica y el soporte o material**"):
    chart_choice = st.multiselect("Seleccione el tipo de gráfico", ("Barras agrupadas", "Dispersión", "Mapa de calor"))
    if "Barras agrupadas" in chart_choice:
        st.markdown("**Muestra el gráfico de barras agrupado por la técnica y el soporte o material**")
        show_grouped_bar_chart()
    if "Dispersión" in chart_choice:
        st.markdown("**Muestra un gráfico de dispersión que indica la relación entre la técnica y el soporte o material**")
        show_scatter_plot()
    if "Mapa de calor" in chart_choice:
        st.markdown("**Muestra un mapa de calor que indica la relación entre la técnica y el soporte o material utilizado**")
        show_heatmap()
if st.sidebar.checkbox("**Nube de palabras**"):
    st.markdown("**Nube de palabras basado en los títulos de las obras de arte**")
    show_wordcloud()
if st.sidebar.checkbox("**Popularidad de la técnica**"):
    st.markdown("**Gráfico de pastel que muestre la proporción de obras de arte creadas con cada técnica**")
    show_technique_popularity()
if st.sidebar.checkbox("**Autores populares**"):
    st.markdown("**Gráfico de barras que muestre la cantidad de obras de arte creadas por cada autor**")
    show_popular_authors()
if st.sidebar.checkbox("**Evolución de la técnica**"):
    st.markdown("**Gráfico de línea que muestre cómo ha evolucionado la técnica utilizada en las obras de arte a lo largo del tiempo**")
    show_plot_technique_evolution()
if st.sidebar.checkbox("**Relación entre la popularidad del autor y la técnica**"):
    st.markdown("**Gráfico de dispersión que muestre la relación entre la popularidad del autor y la técnica utilizada en sus obras de arte**")
    show_plot_author_technique_relation()
if st.sidebar.checkbox("**Relación entre el soporte o material y la popularidad del autor**"):
    st.markdown("**Gráfico de dispersión que muestre la relación entre el material utilizado en las obras de arte y la popularidad del autor que las creó**")
    show_plot_author_material_relation()

    

