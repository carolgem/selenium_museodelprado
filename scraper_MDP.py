# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 10:26:47 2023

@author: cgarcia
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from unidecode import unidecode

#La función toma un elemento y lo procesa para devolver una cadena de caracteres
def process_string(element):
    return ' '.join(element.strip().replace('\n', ' ').split())

#######################################################################
########             WEB SCRAPING: SELENIUM                ############
#######################################################################


#Se está utilizando Selenium con Chrome para abrir un navegador y visitar una página web específica, en este caso el Museo del Prado
browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
browser.get('https://www.museodelprado.es/')

#El panel de las cookies le da click en "Aceptar todas las cookies"
time.sleep(2)
cookies_button = (WebDriverWait(browser, 8)
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,'button#onetrust-accept-btn-handler'))))
cookies_button.click()

#Botón de menú lateral derecha
time.sleep(2)
menu_button = (WebDriverWait(browser, 8)
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,'a.ico_menuppal'))))
menu_button.click()

#Espera hasta que sea clickable el 'Explora la colección'
time.sleep(2)
explore_collection_button = (WebDriverWait(browser, 8)
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="https://www.museodelprado.es/coleccion/obras-de-arte"]'))))
explore_collection_button.click()

#Scroll para buscar 'Escuela' en la página
time.sleep(2)
counter = 0
max_scrolls = 1
element = browser.find_element(By.TAG_NAME, "body")
# Bucle para hacer scroll
while True:
    element.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)
    
    # Incrementar contador
    counter += 1
    
    # Verificar si se alcanzó el número máximo de scrolls
    if counter >= max_scrolls:
        break

#Espera hasta que sea clickable el 'Escuela' 
time.sleep(2)
school_button = (WebDriverWait(browser, 8)
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#ecidoc--has_school---pm--schoolNode span.ico'))))
school_button.click()

#Esperar hasta que se clickable "Ver todos"
time.sleep(2)
see_all_button = (WebDriverWait(browser, 8)
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.open-popup-link.no-close[faceta="2"]'))))
see_all_button.click()

#Escribir en el buscador 'italiana'
time.sleep(2)
search_text = (browser
    .find_element(By.CSS_SELECTOR,'div.buscador-coleccion input[value="Busca por nombre o apellido del autor"][valueaux="Busca por nombre o apellido del autor"][class="texto"]'))
search_text.click()
search_text.clear()
search_text.send_keys('italiana')

#Hacer click en 'italiana'
time.sleep(2)
see_all_button = (WebDriverWait(browser, 8)
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[rel="nofollow"][href="https://www.museodelprado.es/?ecidoc:has_school@@@pm:schoolNode=http://museodelprado.es/items/school_20"][class="faceta"][name="ecidoc:has_school@@@pm:schoolNode=http://museodelprado.es/items/school_20"]'))))
see_all_button.click()

#Hacemos un scroll infinito lento para que se vayan cargando los resultados
time.sleep(2)
# Inicializar contador
counter = 0

# Establecer número máximo de scrolls
max_scrolls = 800
element = browser.find_element(By.TAG_NAME, "body")
# Bucle para hacer scroll
while True:
    element.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)
    
    # Incrementar contador
    counter += 1
    
    # Verificar si se alcanzó el número máximo de scrolls
    if counter >= max_scrolls:
        break

# Mensaje de finalización
print("Finalizado el bucle con éxito después de " + str(counter) + " scrolls.")

#Obtiene el código HTML completo de la página web actualmente visible en el navegador

body = browser.execute_script("return document.body")
source = body.get_attribute('innerHTML')

#iteramos a través de las diferentes obras de arte con beautifulsoup 
image = []
title = []
support = []
author = []

soup = BeautifulSoup(source, "html.parser")

for figure in soup.find_all('div', attrs={'class': 'imgwrap'}):
    image.append(figure.find('img')['src']) 
    
for figure in soup.find_all('figcaption', attrs={'class': 'presentacion-mosaico'}):
    title.append(figure.find('dt').text) 
    support.append(figure.find('dd', attrs={'class': 'soporte'}).text) 
    author.append(figure.find('dd', attrs={'class': 'autor'}).text)

#Crea un diccionario de datos a partir de las listas de imágenes, títulos, soportes y autores y se convierte en un marco de datos de Pandas
data = {'image': image, 'title': title, 'support': support, 'author': author}
df = pd.DataFrame(data)

#######################################################################
########             TRATAMIENTO DE LO DATOS               ############
#######################################################################

# Separa las columna 'support' usando el caracter '.' y crear dos columnas de ella que sean 'materials_process' y 'date'
df['technical_process'] = df['support'].str.split('.').str[0]
df['date'] = df['support'].str.split('.').str[1]

#Eliminamos la columna 'support' una vez se hayan creado de ella 'materials_process' y 'date'
df = df.drop('support', axis=1)

# Crear una función para separar la columna por ',' o 'sobre'
def split_col(col):
    if ',' in col:
        return col.split(',')[0]
    elif 'sobre' in col:
        return col.replace('sobre', ',').split(',')[0]
    else:
        return np.nan

# Aplicar la función a la columna y asignar el resultado a una nueva columna
df['technical'] = df['technical_process'].apply(split_col)

# Crear una función para obtener el texto después de 'sobre'
def get_text_after_sobre(col):
    if 'sobre' in col:
        return col.split('sobre')[-1]
    else:
        return np.nan

# Aplicar la función a la columna y asignar el resultado a una nueva columna
df['support_material'] = df['technical_process'].apply(get_text_after_sobre)

#Eliminamos la columna 'technical_process' una vez se hayan creado de ella 'technical' y 'support_materials'
df = df.drop('technical_process', axis=1)

#Eliminamos las filas con valores faltantes en la columna "date"
df = df.dropna(subset=['date'])

#Reemplazamos todo lo que no sea un 1 o una X al principio de la columna "date" con una cadena vacía
df['date2'] = df['date'].str.replace("^[^1X]*", "")

#Aplicamos una función lambda que elimina el primer caracter '-' y deja solo los primeros 5 caracteres de la columna "date2"
df['date2'] = df['date2'].apply(lambda x: x.replace('-', '', 1)[:5])

#Eliminamos la columna "date" original
df = df.drop('date', axis=1)

#Cambiamos el nombre de la columna "date2" a "date"
df = df.rename(columns={'date2': 'date'})

#Quitamos los espacios de los valores de date para luego reemplazar 
df.date = [row.strip() for row in df.date]

#Reemplazamos los valores de la columna 'date' del dataframe (df) por los valores correspondientes en siglos XIX, XV, XVI, XVII y XVIII.
df['date'] = df['date'].replace({'XIII': '1200','XIX': '1800', 'XV': '1400', 'XVI': '1500', 'XVII': '1600', 'XVIII': '1700'})

df['date'].replace('', 0, inplace=True)

df['date'] = df['date'].astype(int)

df = df[df['date'] != 0]
#Comprobar NAs en columnas
na_count_columns = df.isna().sum()
na_count_columns 

#Eliminar NAs del dataframe
df = df.dropna()
df
#Eliminamos de dataframe las palabras sin acentos, lo que permitirá que el archivo CSV se lea correctamente si lo queremos visualizar en excel.

columns = ['title', 'author','technical', 'support_material']
for column in columns:
    df[column] = df[column].apply(lambda x: unidecode(str(x)))

# la ñ de la columna
df["title"] = df["title"].str.replace("nino", "niño")
df["title"] = df["title"].str.replace("Nino", "Niño")

# Guardar el DataFrame en un archivo CSV con el nombre "artworks.csv"
df.to_csv('artworks.csv', index=False)
print("Dataframe guardado como csv correctamente")
#Cerramos el driver
browser.close()