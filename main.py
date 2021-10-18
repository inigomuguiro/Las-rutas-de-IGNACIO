import streamlit as st 
import pandas as pd
import src.pasos_funciones as pf
from streamlit_folium import folium_static
from PIL import Image
import folium
from geopy.geocoders import Nominatim


image = Image.open("images/rafagas.png")
st.image(image, use_column_width=True)

imagen = Image.open("images/Banner.png")
st.image(imagen, use_column_width=True)

st.write("""
#### Las rutas de IÑAKI pone a disposición de todos los moteros rutas alternativas, evitando la monotonía de las autopistas y recomendando los mejores sitios para comer a lo largo de toda la ruta!
""")
Bilbo = st.sidebar.checkbox("VIAJE AL CENTRO DEL UNIVERSO")
if Bilbo:
    imagen1 = Image.open("images/bilbo.png")
    st.image(imagen1, use_column_width=True)


origen = st.text_input('Ande andas?') 
if not origen:
    st.stop()

destino = st.text_input('Ande vamos?') 
if not destino:
    st.stop()

entrada = pf.dos_puntos(origen, destino)
poly = pf.code_polyline(origen,destino)
puntos = pf.decode_polyline(poly)
restaurantes = pf.rest_ruta(puntos)
centro = pf.centro(puntos)
mapa = pf.map(puntos,centro)

for i in entrada:
    ent = i[0], i[1]
    icon = folium.Icon(color="green", icon="motorcycle", prefix="fa")
    marker = folium.Marker(ent,icon=icon)
    marker.add_to(mapa)




for dic in restaurantes:
    resta = {"location": [dic["Coordenadas"][1],dic["Coordenadas"][0]], "tooltip": dic["Nombre"], "popup":dic["Direccion"] }
    icono = folium.Icon(color="blue", icon="fish", prefix="fa")
    mark = folium.Marker(**resta,icon=icono)
    mark.add_to(mapa)


folium_static(mapa)

#llamamos a la función dos puntos para tener las coordenadas para los markers
#guardamos esas coordenadas en variables para los marker
#llamamos a polyline
#decodificamos poyline
#hacemos la query
#pintamos el mapa con la ruta y los marker de los restaurantes e iniicio fin

