# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:21:21 2023

@author: cgarcia
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import csv

artworks = pd.read_csv('artworks.csv', delimiter = ',')
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
     
selected_century = st.sidebar.selectbox("Seleccione el siglo:", list(siglos.keys()))

st.write("Línea del tiempo agrupada por siglo:")
st.write(f"Siglo {selected_century}:")
for obra in siglos[selected_century]:
     title = obra['title']
     st.write(f"- {title} ({obra['date']})")
     st.image(obra['image'], width=150)