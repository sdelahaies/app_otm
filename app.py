from folium import plugins
#import pymongo as pymongo
from pprint import pprint
#from pymongo import MongoClient
import numpy as np
import random
import pandas as pd
import folium
import streamlit as st
from streamlit_tags import st_tags
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import tkinter as tk
from st_aggrid import AgGrid,ColumnsAutoSizeMode
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from opentrip_api import query_opentripmap
#from kmeans_const import kmeans_plan

from k_means_constrained import KMeansConstrained
#import numpy as np
import math
import streamlit.components.v1 as components


st.set_page_config(layout="wide")


logo = '''
        ▄ ▄▄▄▄▖▄           
     ▟████████████▄        DATASCIENTEST 
   ▟████████████████▙▗     PROJET FIL ROUGE
  ▟█▀      ▐█▘   ▝▀▜██▙          
 ▐█▌ ▗▄▄▄▄▄▟█▙▄▄▄▄  ▝█▙▄   
 ██▌ ▝▀▀▀▀███  ████▖ ▜█▗   ITINERAIRE DE VACANCE
 ███▙▖     ▜█  ████▘ ▐▌▙▘  POI RECOMMANDATION
▝▐███████▌ ▐█  ██▛▘ ▗██ ▌  
 ▀█▌      ▗▟█      ▄██▛▐    
  ▝██████████████████▚▘▘   
    ▜██████████████▚▘▘     WORK_IN_PROGRESS...
       ▀▀▀███▛▀▀▌▝▖▘     
       ▝  ▝▝ ▘ ▝   
'''

colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', \
    'lightred',  'darkblue', 'darkgreen', 'cadetblue', \
    'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', \
    'black', 'lightgray', 'red', 'blue', 'green', 'purple', \
    'orange', 'darkred', 'lightred', 'beige', 'darkblue', \
    'darkgreen', 'cadetblue','beige', 'darkpurple','pink', 'lightblue', \
    'lightgreen', 'gray', 'black', 'lightgray' ]

@st.cache_resource
def print_logo(logo):
    return print(logo)


def init(fname):
    df, list_cities = load_cities(fname)
    df_dest = pd.DataFrame(
        columns=["Non", "latitude", "longitude", "code_postal"])
    df_poi = pd.DataFrame(
        columns=["label", "latitude", "longitude", "activity"])
    df_plan  = pd.DataFrame({'a' : []})
    return df, list_cities, df_dest, df_poi,df_plan


@st.cache_data
def load_cities(fname):
    df = pd.read_csv("cities.csv")
    list_cities = pd.unique(df["Nom"]).tolist()
    return df, list_cities


@st.cache_resource
def get_city(city_keyword):
    city_keyword = [k.upper() for k in city_keyword]
    return df[df["Nom"].isin(city_keyword)], city_keyword


@st.cache_resource
def set_marker(label, lat, lon, col):
    return folium.Marker(
        location=[lat, lon],
        popup=f"{label}: ({lat:.2f}, {lon:.2f})",
        icon=folium.Icon(color=col, icon="hamburger", prefix='fa'),)
    
@st.cache_resource
def get_marker(poi):
    coord = poi["geometry.coordinates"]
    lon = float(coord.split(',')[0][1:])
    lat = float(coord.split(',')[1][1:-1])
    #lon = poi["geometry.coordinates"][0]
    #lat = poi["geometry.coordinates"][1]
    return folium.Marker(
        location=[lat, lon],
        popup=f"({lat:.2f}, {lon:.2f})",
        icon=folium.Icon(color="red", icon="hamburger", prefix='fa'))    


# # @st.cache_data
# def poi_info(poi):
#     if "Restaurant" in poi["type"]:
#         poiType = "Restaurant"
#     elif "Event" in poi["type"]:
#         poiType = "Event"
#     elif "Accommodation" in poi["type"]:
#         poiType = "Accommodation"
#     elif "CulturalSite" in poi["type"]:
#         poiType = "CulturalSite"
#     elif "Tour" in poi["type"]:
#         poiType = "Tour"
#     else:
#         poiType = "misc."
#     return [
#         poi["label"],
#         float(poi["location"]["coordinates"][1]),
#         float(poi["location"]["coordinates"][0]),
#         poiType,poi["descriptionFR"]
 #   ]

# @st.cache_data
# def poi_col(poiInfo):
#     if poiInfo[-2] == "Restaurant":
#         return "red"
#     if poiInfo[-2] == "Event":
#         return "purple"
#     if poiInfo[-2] == "Accommodation":
#         return "blue"
#     if poiInfo[-2] == "CulturalSite":
#         return "lightblue"
#     if poiInfo[-2] == "Tour":
#         return "purple"
#     if poiInfo[-2] == "misc.":
#         return "orange"


    

@st.cache_resource
def get_POIs(city_keyword, poi_keyword,nb_poi,radius):
    markers_list = []
    df_dest, city_keyword = get_city(city_keyword)
    poi_list = []
    for index, row in df_dest.iterrows():
        marker = set_marker(row.Nom, float(row.latitude),
                            float(row.longitude), "green")
        markers_list.append(marker)
        df_query = query_opentripmap(float(row.latitude),float(row.longitude))
        markers_list.extend(get_marker(poi) for i, poi in df_query.iterrows())
    return df_dest, city_keyword, markers_list, df_query

@st.cache_resource
def load_POIs():
    markers_list = []
    df_dest = pd.read_csv("tmp_dest.csv")
    poi_list = []
    for index, row in df_dest.iterrows():
        marker = set_marker(row.Nom, float(row.latitude),
                            float(row.longitude), "green")
        markers_list.append(marker)
        #df_query = query_opentripmap(float(row.latitude),float(row.longitude))
        df_query = pd.read_csv("tmp_poi.csv")
        markers_list.extend(get_marker(poi) for i, poi in df_query.iterrows())
    return df_dest, markers_list, df_query

@st.cache_resource
def get_center(df_poi):
    sw = df_poi[['latitude', 'longitude']].min().values.tolist()
    ne = df_poi[['latitude', 'longitude']].max().values.tolist()
    x = 0.5*(sw[0]+ne[0])
    y = 0.5*(sw[1]+ne[1])
    return [x, y]

@st.cache_resource
def kmeans_plan(df,nmin=3,nmax=6):
    X = np.array(df[["lat","lon"]])
    ndays = math.ceil(len(df)/4)
    clf = KMeansConstrained(
        n_clusters=ndays,
        size_min=nmin,
        size_max=nmax,
        random_state=42
    )
    clf.fit_predict(X)
    labels = clf.labels_
    df['cluster'] = labels
    
    txt ='<div style="background-color:#cde1f8">'
    for i in range(ndays):
        txt = txt+f'<p style="color:{colors[i]};"><b>Jour {i+1}:</b></p>\n'
        df_cluster = df[df.cluster==i]
        for _, row in df_cluster.iterrows():
            txt = txt+f"<li>{row['properties.name']} {row['properties.xid']}</li>\n"
    txt=txt+'</div>'
    return df, txt

print_logo(logo)
fname = "cities.csv"
df, list_cities, df_dest, df_poi, df_plan = init(fname)

# does not seem to work on a VM since no display attached
#root = tk.Tk()
#screen_width = root.winfo_screenwidth()
# you may want to adapt to your screen resolution
screen_width = 1920

CENTER_START = [46.2, 1.82]
ZOOM_START = 6


list_type = ["toute activité", "hébergement",
             "restauration", "musée", "tous", "..."]
if "txt" not in st.session_state:
    st.session_state["txt"] = ""
if "plan" not in st.session_state:
    st.session_state["plan"] = df_plan
if "markers" not in st.session_state:
    st.session_state["markers"] = []
if "destinations" not in st.session_state:
    st.session_state["destinations"] = df_dest
if "POIs" not in st.session_state:
    st.session_state["POIs"] = df_poi
if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START
if "zoom" not in st.session_state:
    st.session_state["zoom"] = ZOOM_START

st.title("Recommandation d'activités")

city_keyword = st_tags(label='Destination:',
                       text='Ajouter une ou plusieurs villes de destination',
                       value=['CONDAT SUR VEZERE'],
                       suggestions=list_cities,
                       maxtags=4,
                       key="destination")

#colA, colB, colC ,colD= st.columns(4, gap="small")
#with colA:
#    poi_keyword = st.multiselect(label="Choisissez un type de lieu, activité ou évènement",
#                                 options=['Tout', 'Restaurant', 'Accommodation', 'Tour', 'CulturalSite', 'misc.'])

#with colB:
#    timePeriod = st.date_input(
#        label="Date de départ-date de retour",
#        value=[datetime.now(), datetime.now() + timedelta(days=7)]
#    )
#with colC:
#    nb_poi = st.number_input(
#        label='Nombre de POI par destination', format="%i", value=10)
#with colD:
#    radius = st.number_input(
#        label='Rayon autour de la destination (km)', format="%f", value=5.0,step=0.1)



col1, col2, col3, col4, col5 = st.columns(5, gap="small")
with col1:
    col11, col12 = st.columns(2, gap="small")
    with col11:
        if st.button('**valider**'):
            #df_dest, city_keyword, POIs, df_poi = get_POIs(
            #    city_keyword, poi_keyword,nb_poi,radius)
            df_dest, POIs,df_poi = load_POIs()
            df_dest.to_csv("tmp_dest.csv",index=False)
            df_poi.to_csv("tmp_poi.csv",index=False)
            st.session_state["destinations"] = df_dest
            st.session_state["POIs"] = df_poi
            for poi in POIs:
                st.session_state["markers"].append(poi)
            #st.session_state["center"] = get_center(df_poi)
            st.session_state["zoom"] = 12

    with col12:
        if st.button('**annuler**'):
            st.session_state["markers"] = []


m = folium.Map(location=CENTER_START, zoom_start=8)
fg_mark = folium.FeatureGroup(name="Markers")
for marker in st.session_state["markers"]:
    fg_mark.add_child(marker)
st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="new",
    feature_group_to_add=fg_mark,
    height=700,
    width=screen_width,
)

#st.markdown("Destinations")
#AgGrid(st.session_state["destinations"], columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,enable_enterprise_modules=False)
st.write(st.session_state["destinations"])

#colA1, colA2 = st.columns(2, gap="small")

#with colA1:
st.markdown("Points d'intérets")
#AgGrid(st.session_state["POIs"], columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,enable_enterprise_modules=False)
df_POIs = st.session_state["POIs"] #[["properties.xid","properties.name","properties.dist","properties.rate","properties.kinds"]]
gd = GridOptionsBuilder.from_dataframe(df_POIs)
gd.configure_selection(selection_mode='multiple', use_checkbox=True)
gridoptions = gd.build()
#gd.configure_column('properties.xid', suppressToolPanel=True)
grid_table = AgGrid(df_POIs, height=300,gridOptions=gridoptions,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                    enable_enterprise_modules=False)

# with colA2:
selected_row = grid_table["selected_rows"]
st.write(f'{len(selected_row)} points sélectionnés')
#st.dataframe(selected_row)
#st.text(selected_row[0]["geometry.coordinates"])
#st.text(selected_row[0])


#st.write(df)
#st.write(df["lon"][0])

if st.button('**Plan**'):
    df = pd.DataFrame.from_dict(selected_row)
    df["lat"]=df["geometry.coordinates"].apply(lambda x: float(x.split(',')[1][1:-1]))
    df["lon"]=df["geometry.coordinates"].apply(lambda x: float(x.split(',')[0][1:]))
    df_plan,txt = kmeans_plan(df)
    st.session_state["plan"] = df_plan
    st.session_state["txt"] = txt

#st.write(st.session_state["plan"])

m2 = folium.Map(location=CENTER_START, zoom_start=8)
fg_mark2 = folium.FeatureGroup(name="Markers")
if not st.session_state["plan"].empty:
    for _, row in st.session_state["plan"].iterrows():
        marker = set_marker("", row["lat"], row["lon"], colors[row["cluster"]])
        fg_mark2.add_child(marker)

colB1, colB2 = st.columns(2, gap="small")
with colB1:
    st_folium(
        m2,
        center=st.session_state["center"],
        zoom=st.session_state["zoom"],
        #key="new",
        feature_group_to_add=fg_mark2,
        height=700,
        width=screen_width,
    )
with colB2:
    components.html(st.session_state["txt"], width=600,height=700,scrolling=True)