import pandas as pandas
import geopandas as gpd
from pymongo import MongoClient
import numpy as np
import shapely
import json
from geopy.geocoders import Nominatim
from time import sleep
import requests
import folium
from folium import Choropleth, Circle, Marker, Icon, map

from config.configuration import collection


def dos_puntos(origin, destination):
    geolocator = Nominatim(user_agent="coordenadas")
    coord_origin = geolocator.geocode(origin)
    coord_destination = geolocator.geocode(destination)
    lista = [[coord_origin.latitude, coord_origin.longitude], [coord_destination.latitude, coord_destination.longitude]]
    return lista

def code_polyline(origen,destino):
    key = "AIzaSyBIVYzGm2OnB-ZxrsPGUmxz-ERUP_Jtkxc" #luego coger de .env
    web = "https://maps.googleapis.com/maps/api/directions/json?origin="
    web1 = "&destination="
    web2 = "&avoid=highways&key="
    todas = web+origen+web1+destino+web2+key
    sale = requests.get(todas).json()
    code = sale["routes"][0]["overview_polyline"]["points"]
    return code

def decode_polyline(polyline_str):
    '''Pass a Google Maps encoded polyline string; returns list of lat/lon pairs'''
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']: 
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates

# This function requires Esri's arcpy module.
def convert_to_shapefile(steps, output_shapefile):
    '''Pass the steps object returned by the Maps API (should be response['routes'][0]['legs'][0]['steps'])
    and an output shapefile path; outputs a detailed shapefile of that route'''
    
    import arcpy
    import os

    # Decode each step of the route; add those coordinate pairs to a list
    total_route = []
    for step in steps:
        total_route += decode_polyline(step['polyline']['points'])

    # Create empty WGS84 shapefile.
    sr = arcpy.SpatialReference(4326)
    arcpy.CreateFeatureclass_management(os.path.dirname(output_shapefile), os.path.basename(output_shapefile), 
        "POLYLINE", spatial_reference=sr)

    # Add points to array, write array to shapefile as a polyline
    arr = arcpy.Array()
    for coord_pair in total_route:
        arr.add(arcpy.Point(coord_pair[1], coord_pair[0]))
    with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@']) as rows:
        rows.insertRow([arcpy.Polyline(arr)])
    del rows

    return output_shapefile

def rest_ruta(point_list):
    lista = []
    for point in point_list:
        #print(point[0], point[1])
        
        query = {"geometry": {"$near": {"$geometry": {"type": "Point", "coordinates" : [point[1], point[0]]},
                                "$minDistance":100 ,"$maxDistance": 4000}}}
        proj = {"Nombre": 1, "Direccion":1, "Coordenadas":1, "_id":0}
        resultados = list(collection.find(query,proj))
        if len(resultados) != 0:
            lista.append(resultados[0])
    final = [dict(elemento) for elemento in {tuple(d.items()) for d in lista}]
    # turn to dict the Coordenadas json
    for f in final:
        f["Coordenadas"] = json.loads(f["Coordenadas"].replace("'", '"')).get("coordinates")
    return final

def centro(puntos_mapa):
    pos = len(puntos_mapa)//2
    return list(puntos_mapa[pos])

def map(datitos, loc_inicial):
    m = folium.Map(location=loc_inicial, zoom_start=8, tiles='Stamen Terrain')
    folium.PolyLine(datitos, color='blue').add_to(m)
    return m



    """
    for r in restaurantes:
        name = r.get("Nombre")
        address = r.get("Direccion")
        coords = r.get("Coordenadas")
        folium.Marker(location=[coords[1], coords[0]], popup=address, tooltip=name).add_to(m)
        m
    """