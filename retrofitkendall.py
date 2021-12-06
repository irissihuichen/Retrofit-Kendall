import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# Read csv file
fp = 'https://raw.githubusercontent.com/irissihuichen/Retrofit-Kendall/main/kendall_new2.csv'
df = pd.read_csv(fp)

# Calculate the differences of 3 index
df['dif1_EUI'] = df['tEUI_base'] - df['tEUI_con']
df['dif2_EUI'] = df['tEUI_base'] - df['tEUI_DE']
df['dif3_EUI'] = df['tEUI_base'] - df['tEUI_DEP']
df['dif1_CO2e'] = df['tCO2e_base'] - df['tCO2e_con']
df['dif2_CO2e'] = df['tCO2e_base'] - df['tCO2e_DE']
df['dif3_CO2e'] = df['tCO2e_base'] - df['tCO2e_DEP']
df['dif1_COST'] = df['tCOST_con'] 
df['dif2_COST'] = df['tCOST_DE'] 
df['dif3_COST'] = df['tCOST_DEP'] 

# Calculate the 3 total maximized sum
max_dif_EUI = df['dif3_EUI'].sum()
max_dif_CO2e = df['dif3_CO2e'].sum()
max_dif_COST = df['dif3_COST'].sum()

# Sort the data ascending by vintage
df_office = df.loc[df['type']=='Office'].sort_values(['vintage'], ascending=False)
df_housing = df.loc[df['type']=='Housing'].sort_values(['vintage'], ascending=False)
df_lab = df.loc[df['type']=='Laboratory'].sort_values(['vintage'], ascending=False)

# Max sums for each type and for each index
max_dif_EUI_housing = df_housing['dif3_EUI'].sum()
max_dif_EUI_office = df_office['dif3_EUI'].sum()
max_dif_EUI_lab = df_lab['dif3_EUI'].sum()
max_dif_CO2e_housing = df_housing['dif3_CO2e'].sum()
max_dif_CO2e_office = df_office['dif3_CO2e'].sum()
max_dif_CO2e_lab = df_lab['dif3_CO2e'].sum()
max_dif_COST_housing = df_housing['dif3_COST'].sum()
max_dif_COST_office = df_office['dif3_COST'].sum()
max_dif_COST_lab = df_lab['dif3_COST'].sum()


# Define functions for converting differences into percentages in the max
def calculate_percent_office(level,index,val):
  if level == 'Conventional':
    if index == 'EUI':
      return df_office['dif1_EUI'].sample(frac=val).sum()/max_dif_EUI_office
    elif index == 'CO2e':
      return df_office['dif1_CO2e'].sample(frac=val).sum()/max_dif_CO2e_office
    else:
      return df_office['dif1_COST'].sample(frac=val).sum()/max_dif_COST_office
  elif level == 'Deep Energy':
    if index == 'EUI':
      return df_office['dif2_EUI'].sample(frac=val).sum()/max_dif_EUI_office
    elif index == 'CO2e':
      return df_office['dif2_CO2e'].sample(frac=val).sum()/max_dif_CO2e_office
    else:
      return df_office['dif2_COST'].sample(frac=val).sum()/max_dif_COST_office    
  elif level == 'Deep Energy Plus':
    if index == 'EUI':
      return df_office['dif3_EUI'].sample(frac=val).sum()/max_dif_EUI_office
    elif index == 'CO2e':
      return df_office['dif3_CO2e'].sample(frac=val).sum()/max_dif_CO2e_office
    else:
      return df_office['dif3_COST'].sample(frac=val).sum()/max_dif_COST_office 

def calculate_percent_housing(level,index,val):
  if level == 'Conventional':
    if index == 'EUI':
      return df_housing['dif1_EUI'].sample(frac=val).sum()/max_dif_EUI_housing
    elif index == 'CO2e':
      return df_housing['dif1_CO2e'].sample(frac=val).sum()/max_dif_CO2e_housing
    else:
      return df_housing['dif1_COST'].sample(frac=val).sum()/max_dif_COST_housing
  elif level == 'Deep Energy':
    if index == 'EUI':
      return df_housing['dif2_EUI'].sample(frac=val).sum()/max_dif_EUI_housing
    elif index == 'CO2e':
      return df_housing['dif2_CO2e'].sample(frac=val).sum()/max_dif_CO2e_housing
    else:
      return df_housing['dif2_COST'].sample(frac=val).sum()/max_dif_COST_housing    
  elif level == 'Deep Energy Plus':
    if index == 'EUI':
      return df_housing['dif3_EUI'].sample(frac=val).sum()/max_dif_EUI_housing
    elif index == 'CO2e':
      return df_housing['dif3_CO2e'].sample(frac=val).sum()/max_dif_CO2e_housing
    else:
      return df_housing['dif3_COST'].sample(frac=val).sum()/max_dif_COST_housing 

def calculate_percent_lab(level,index,val):
  if level == 'Conventional':
    if index == 'EUI':
      return df_lab['dif1_EUI'].sample(frac=val).sum()/max_dif_EUI_lab
    elif index == 'CO2e':
      return df_lab['dif1_CO2e'].sample(frac=val).sum()/max_dif_CO2e_lab
    else:
      return df_lab['dif1_COST'].sample(frac=val).sum()/max_dif_COST_lab
  elif level == 'Deep Energy':
    if index == 'EUI':
      return df_lab['dif2_EUI'].sample(frac=val).sum()/max_dif_EUI_lab
    elif index == 'CO2e':
      return df_lab['dif2_CO2e'].sample(frac=val).sum()/max_dif_CO2e_lab
    else:
      return df_lab['dif2_COST'].sample(frac=val).sum()/max_dif_COST_lab   
  elif level == 'Deep Energy Plus':
    if index == 'EUI':
      return df_lab['dif3_EUI'].sample(frac=val).sum()/max_dif_EUI_lab
    elif index == 'CO2e':
      return df_lab['dif3_CO2e'].sample(frac=val).sum()/max_dif_CO2e_lab
    else:
      return df_lab['dif3_COST'].sample(frac=val).sum()/max_dif_COST_lab
  elif level == 'Base':
      return value=='0.00'


st.write('# Retrofitting Kendall Square')

# Multiple trace radar chart

categories = ['housing','office','laboratory','housing']
retrofit = ['Base Case', 'Conventional', 'Deep Energy', 'Deep Energy Plus']

# Tick box
st.sidebar.markdown('#### Retrofitting Level')

eui = 'EUI'
cost = 'COST'
co2e = 'CO2e'

# Radar chart
def radar_chart(retrofit,val): 
    fig = go.Figure()

    # Fix the same numbers for line start and end
    r_housing_eui = round(calculate_percent_housing(retrofit,eui,val),2)
    r_housing_cost = round(calculate_percent_housing(retrofit,cost,val),2)
    r_housing_co2e = round(calculate_percent_housing(retrofit,co2e,val),2)

    fig.add_trace(go.Scatterpolar(
          r=[r_housing_eui,
       round(calculate_percent_office(retrofit,eui,val),2),
       round(calculate_percent_lab(retrofit,eui,val),2),
       r_housing_eui],
          theta=categories,
          type= 'scatterpolar',
          mode='lines',
          line_color='rgba(92, 140, 255, 0.8)',
          #fill='toself',
          #fillcolor='rgba(92, 140, 255, 0.8)',
          name='EUI'
    ))
    fig.add_trace(go.Scatterpolar(
          r=[r_housing_cost,
       round(calculate_percent_office(retrofit,cost,val),2),
       round(calculate_percent_lab(retrofit,cost,val),2),
       r_housing_cost],
          theta=categories,
          type= 'scatterpolar',
          mode='lines',
          line_color='rgba(255, 56, 75, 0.66)',
          #fill='toself',
          #fillcolor='rgba(255, 212, 97, 0.6)',
          name='COST'
    ))
    fig.add_trace(go.Scatterpolar(
          r=[r_housing_co2e,
       round(calculate_percent_office(retrofit,co2e,val),2),
       round(calculate_percent_lab(retrofit,co2e,val),2),
       r_housing_co2e],
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


if __name__ == '__main__':
    val = st.sidebar.slider('Select value',0.0,1.0,0.1)
    RL = st.sidebar.radio('Select the retrofit level', retrofit, index=1)
    radar_chart(RL,val)
