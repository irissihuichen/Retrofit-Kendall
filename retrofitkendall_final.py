
# Import from installed libraries
import csv
import json
import math
from PIL import Image
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import geopandas as gpd
import pandas as pd 
from geopandas import GeoDataFrame

import numpy as np 
import urllib.request as ur 
from urllib.error import URLError

import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go


########## Create new dataframes responding to sliders and checkboxes 
# Read from the github raw link
fp = 'https://raw.githubusercontent.com/irissihuichen/Retrofit-Kendall/main/kendall_new_updated.csv'
df = pd.read_csv(fp)

# Convert str into readable coordinates
raw_final = []
for i in range(len(df)):
  str = df.geometry[i]
  raw = str.split(',')
  raw[0] = raw[0].split('(')[-1]
  raw[-1] = raw[-1].split(')')[0]
  raw_2 = []
  for j in range(len(raw)):
    n = raw[j].split(' ')
    raw_2.append([float(n[-2]), float(n[-1])])
  raw_final.append(raw_2)

# Add it back to dataframe
df['coordinates'] = raw_final

########## Update data for correct extrusion heights and radius in map
df['ntEUI_base'] = df['tEUI_base'] / 10000
df['ntEUI_con'] = df['tEUI_con'] / 10000
df['ntEUI_DE'] = df['tEUI_DE'] / 10000
df['ntEUI_DEP'] = df['tEUI_DEP'] / 10000
df['ntcost_base'] = df['tcost_base'] / 6000
df['ntcost_con'] = df['tcost_con'] / 6000
df['ntcost_DE'] = df['tcost_DE'] / 6000
df['ntcost_DEP'] = df['tcost_DEP'] / 6000
df['nthealth_base'] = df['thealth_base'] / 5000
df['nthealth_con'] = df['thealth_con'] / 5000
df['nthealth_DE'] = df['thealth_DE'] / 5000
df['nthealth_DEP'] = df['thealth_DEP'] / 5000

########### Start writing the App 
st.write("""# Kendall Square Retrofit""")
st.write('This app helps to predict the effect of building retrofit in energy use/carbon emission, health impacts and investment costs of the Kendall/MIT area.')

########## Create sliders ##########
# Slider anno
st.sidebar.header('Changing Retrofit Parameters')
st.sidebar.markdown('#### Retrofitting Percentage')
# Slider control for 3 types  
     ######### Variants
s_office = st.sidebar.slider('office',0.0,1.0,step=0.1)
s_housing = st.sidebar.slider('housing',0.0,1.0,step=0.1)
s_lab =  st.sidebar.slider('laboratory',0.0,1.0,step=0.1)

########## Create checkboxes ##########
# Checkbox anno
st.sidebar.markdown('#### Retrofitting Level')
# Define the 4 levels
check_level = ['Base Case', 'Conventional', 'Deep Energy', 'Deep Energy Plus']
# Display checkboxes
     ######### Variants
levelchecked = st.sidebar.radio('select a level to test', check_level, index=1)

# Calculate differences from base EUI 
df['tEUIdif_con'] = df['tEUI_base'] - df['tEUI_con']
df['tEUIdif_DE'] = df['tEUI_base'] - df['tEUI_DE']
df['tEUIdif_DEP'] = df['tEUI_base'] - df['tEUI_DEP']

# Subdivide dataframe into 3 by building types sorted by vintage
df_office = df.loc[df['type']=='Office'].sort_values(['vintage'], ascending=False)
df_housing = df.loc[df['type']=='Housing'].sort_values(['vintage'], ascending=False)
df_lab = df.loc[df['type']=='Laboratory'].sort_values(['vintage'], ascending=False)

# Select data based on slider percentage variants
office_sel = df_office.head(round(s_office*len(df_office)))
housing_sel = df_housing.head(round(s_housing*len(df_housing)))
lab_sel = df_lab.head(round(s_lab*len(df_lab)))

# Collect the unselected
office_un = df_office.head(round((1-s_office)*len(df_office)))
housing_un = df_housing.head(round((1-s_housing)*len(df_housing)))
lab_un = df_lab.head(round((1-s_lab)*len(df_lab)))

# Create a list 
sel = [office_sel, housing_sel, lab_sel]
un = [office_un, housing_un, lab_un]

# Create a new dataframe from the selected
df_sel = pd.concat(sel)
df_un = pd.concat(un)

# Clear values of the unselected to base values
df_un['ntEUI_con'] = df_un.apply(lambda x: x['ntEUI_base'], axis=1)
df_un['ntEUI_DE'] = df_un.apply(lambda x: x['ntEUI_base'], axis=1)
df_un['ntEUI_DEP'] = df_un.apply(lambda x: x['ntEUI_base'], axis=1)

df_un['nthealth_con'] = df_un.apply(lambda x: x['nthealth_base'], axis=1)
df_un['nthealth_DE'] = df_un.apply(lambda x: x['nthealth_base'], axis=1)
df_un['nthealth_DEP'] = df_un.apply(lambda x: x['nthealth_base'], axis=1)

df_un['ntcost_con'] = df_un.apply(lambda x: x['ntcost_base'], axis=1)
df_un['ntcost_DE'] = df_un.apply(lambda x: x['ntcost_base'], axis=1)
df_un['ntcost_DEP'] = df_un.apply(lambda x: x['ntcost_base'], axis=1)

# Further create dataframes by index
## Create a new dictionary to convert 'check_level' into column names in dataframe
convert = {'Base Case':'base', 'Conventional':'con', 'Deep Energy':'DE', 'Deep Energy Plus':'DEP'}

## Adapt to the original name format for the checkbox variants
eui = 'ntEUI_' + convert[levelchecked]
cost = 'ntcost_' + convert[levelchecked]
health = 'nthealth_' + convert[levelchecked]

# Merge dataframes
all = [df_sel, df_un]
df_all = pd.concat(all)

# Coordinates, lat, lon, index
df_eui = df_all[['coordinates','lat','lon',eui]]
df_cost = df_all[['coordinates','lat','lon',cost]]
df_health = df_all[['coordinates','lat','lon',health]]

# Convert to json files to be used in mapping
file_eui = df_eui.to_json(orient = 'records')
file_cost = df_cost.to_json(orient = 'records')
file_health = df_health.to_json(orient = 'records')


# Create color gradients: red to blue
## https://colordesigner.io/gradient-generator
color_gradients = [
                   [0,255,0],
                   [116,186,0],
                   [231,243,0],
                   [255,244,0],
                   [255,229,0],
                   [255,215,0],
                   [255,201,0],
                   [255,186,0],
                   [255,172,0],
                   [255,158,0],
                   [255,143,0],
                   [255,129,0],
                   [255,115,0],
                   [255,100,0],
                   [255,86,0],
                   [255,72,0],
                   [255,57,0],
                   [255,43,0],
                   [255,29,0],
                   [255,14,0],
                   [255,0,0],
]

# Reverse gradient change
color_gradients_r = color_gradients[::-1]

# Divide the range by the gradient number 21
eui_color = np.linspace(16, 1122, num=21).tolist()
health_color = np.linspace(10, 681, num=21).tolist()

# Define function to assign color gradient for its location in the range
## Carbon gradient change
### enumerate() works with any iterable; pythonic way to loop over
### i as count, b as value
def assign_gradient_eui(val):
  for i, b in enumerate(eui_color):
    if val < b:
      return color_gradients[i]
    else:
      i+=1
  return color_gradients[i]

## Health reversed gradient change
def assign_gradient_health(val):
  for i, b in enumerate(health_color):
    if val < b:
      return color_gradients_r[i]
    else:
      i+=1
  return color_gradients_r[i]

# Define fill color by gradient function
df_eui['fill_color'] = df_eui[eui].apply(lambda x: assign_gradient_eui(x))
df_health['fill_color'] = df_health[health].apply(lambda x: assign_gradient_health(x))


########## Create Maps ##########
# Create a 2-column layout in App to show 2 maps side by side
## Proportion 1 : 1
col_1, col_2 = st.columns((1,1))

# Map 1 in column 1
with col_1:
  # Tittle
  col_1.subheader('**Energy Use Intensity**')
  col_1.markdown("EUI * building total area (kBtu)")

  # Create map 1: eui and carbon 
  try:
    layers = {
            # EUI extrusion             
            'Total EUI': pdk.Layer(
                'PolygonLayer',
                df_eui,
                opacity=0.4,
                stroked=True,
                get_position=['lon', 'lat'], 
                get_polygon='coordinates',
                filled=True,
                extruded=True,
                wireframe=True,
                get_elevation=eui,
                get_fill_color= 'fill_color',
                get_line_color='fill_color',
                auto_highlight=False,
                pickable=True),    

            # Cost circles
            'Retrofit Cost': pdk.Layer(
                "ScatterplotLayer",
                df_cost,
                get_position=['lon', 'lat'],
                get_color=[200, 30, 0, 160],
                get_radius=cost,
                radius_scale=0.2)  
    }
    st.sidebar.markdown('### EUI Map')
    selected_layers = [
            layer for layer_name, layer in layers.items()
            if st.sidebar.checkbox(layer_name, True)]
    if selected_layers:
        st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state={'latitude': 42.36, 'longitude': -71.085, 'zoom': 13, 'pitch': 50},
                layers=selected_layers,))
    else:
        st.error("Please choose at least one layer above.")
  except URLError as e:
    st.error('Error')

# Map 2 in column 2
with col_2:
  # Tittle
  col_2.subheader('**Health Improvement**')
  col_2.markdown("Air change hour (s)")

  # Create 2nd map: cost and health 
  try:
    layers = {
            # Health extrusion             
            'Cost': pdk.Layer(
                'PolygonLayer',
                df_health,
                opacity=0.3,
                stroked=True,
                get_position=['lon', 'lat'], 
                get_polygon='coordinates',
                filled=True,
                extruded=True,
                wireframe=True,
                get_elevation=health,
                get_fill_color= 'fill_color',
                get_line_color='fill_color',
                auto_highlight=False,
                pickable=True)             
    }
    st.sidebar.markdown('### Health Map')
    selected_layers = [
            layer for layer_name, layer in layers.items()
            if st.sidebar.checkbox(layer_name, True)]
    if selected_layers:
        st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state={'latitude': 42.36,'longitude': -71.085, 'zoom': 13, 'pitch': 50},
                layers=selected_layers,))
    else:
        st.error("Please choose at least one layer above.")
  except URLError as e:
    st.error('Error')

##########  Add gradiant bar anno image at the bottom ##########
#image = Image.open('https://raw.githubusercontent.com/irissihuichen/Retrofit-Kendall/main/colorbar.png','r')
st.image('https://raw.githubusercontent.com/irissihuichen/Retrofit-Kendall/main/colorbar.png',width=450)


################### Create Radar Charts ##########################
# Max sums for each type and for each index
max_dif_EUI_housing = df_housing['tEUIdif_DEP'].sum()
max_dif_EUI_office = df_office['tEUIdif_DEP'].sum()
max_dif_EUI_lab = df_lab['tEUIdif_DEP'].sum()
max_dif_health_housing = df_housing['thealth_DEP'].sum()
max_dif_health_office = df_office['thealth_DEP'].sum()
max_dif_health_lab = df_lab['thealth_DEP'].sum()
max_dif_cost_housing = df_housing['tcost_DEP'].sum()
max_dif_cost_office = df_office['tcost_DEP'].sum()
max_dif_cost_lab = df_lab['tcost_DEP'].sum()

# Adapt to the original name format from the variant
eui2 = 'tEUIdif_' + convert[levelchecked]
cost2 = 'tcost_' + convert[levelchecked]
health2 = 'thealth_' + convert[levelchecked]

# Define functions for converting differences into percentages in the max
def calculate_percent_office(level,index):
  if index == 'EUI':
    return office_sel[eui2].sum()/max_dif_EUI_office
  elif index == 'health':
    return office_sel[health2].sum()/max_dif_health_office
  elif index == 'cost':
    return office_sel[cost2].sum()/max_dif_cost_office
  else:
    return Error

def calculate_percent_housing(level,index):
  if index == 'EUI':
    return housing_sel[eui2].sum()/max_dif_EUI_housing
  elif index == 'health':
    return housing_sel[health2].sum()/max_dif_health_housing
  elif index == 'cost':
    return housing_sel[cost2].sum()/max_dif_cost_housing
  else:
    return Error

def calculate_percent_lab(level,index):
  if index == 'EUI':
    return lab_sel[eui2].sum()/max_dif_EUI_lab
  elif index == 'health':
    return lab_sel[health2].sum()/max_dif_health_lab
  elif index == 'cost':
    return lab_sel[cost2].sum()/max_dif_cost_lab
  else:
    return Error

# Define index
i_eui = 'EUI'
i_health = 'health'
i_cost = 'cost'

# Multiple trace radar chart
categories = ['housing','office','laboratory','housing']     

##################### Radar chart #####################
# Tittle
st.subheader('**Value Comaprison**')
st.markdown("Percentages of effect within the maximum potential")
try: 
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
          r=[round(calculate_percent_office(levelchecked,i_eui),2),
        round(calculate_percent_housing(levelchecked,i_eui),2),
        round(calculate_percent_lab(levelchecked,i_eui),2),
        round(calculate_percent_office(levelchecked,i_eui),2)],
           theta=categories,
           type= 'scatterpolar',
           mode='lines',
           line_color='rgba(92, 140, 255, 0.8)',
           #fill='toself',
           #fillcolor='rgba(92, 140, 255, 0.8)',            
           name='EUI'
    ))
    fig.add_trace(go.Scatterpolar(
          r=[round(calculate_percent_office(levelchecked,i_cost),2),
        round(calculate_percent_housing(levelchecked,i_cost),2),
        round(calculate_percent_lab(levelchecked,i_cost),2),
        round(calculate_percent_office(levelchecked,i_cost),2)],
           theta=categories,
           type= 'scatterpolar',
           mode='lines',
           line_color='rgba(255, 56, 75, 0.66)',
           #fill='toself',
           #fillcolor='rgba(255, 212, 97, 0.6)',
           name='COST'
    ))
    fig.add_trace(go.Scatterpolar(
           r=[round(calculate_percent_office(levelchecked,i_health),2),
        round(calculate_percent_housing(levelchecked,i_health),2),
        round(calculate_percent_lab(levelchecked,i_health),2),
        round(calculate_percent_office(levelchecked,i_health),2)],
           theta=categories,
           type= 'scatterpolar',
           mode='lines',
           line_color='rgba(0, 130, 120, 0.5)',
           #fill='toself',
           #fillcolor='rgba(112, 230, 195, 0.6)',
           name='HEALTH'
    ))
    fig.update_layout(
     polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0,1]
        )),
        showlegend=False
      )
    st.write(fig)

except URLError as e:
    st.error('Error') 

##########  Add development path diagram ##########
st.subheader('**Development Path**')
st.markdown("Development stages supported by different tools or media")
st.image('https://raw.githubusercontent.com/irissihuichen/Retrofit-Kendall/main/Retrofitmodel.jpg',width=800)