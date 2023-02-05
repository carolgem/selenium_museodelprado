# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:21:19 2023

@author: cgarcia
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import csv

artworks = pd.read_csv('artworks.csv', delimiter = ',')
titulo_cuadro = st.selectbox("Seleccione un cuadro", artworks["title"])

selected_row = artworks[artworks["title"] == titulo_cuadro]

st.write("Título: ", selected_row["title"].values[0])
st.write("Autor: ", selected_row["author"].values[0])
st.write("Técnica: ", selected_row["technical"].values[0])
st.write("Soporte/Material: ", selected_row["support_material"].values[0])
st.write("Año: ", selected_row["date"].values[0])

st.image(selected_row["image"].values[0], width=250)