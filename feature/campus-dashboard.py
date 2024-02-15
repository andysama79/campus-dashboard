import streamlit as st
import pdb
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import configparser

from campus_energy import get_last_n_readings, get_reading_for_days
from campus_weather import get_current_data, get_df_for_timeperiod

import plotly.express as px
import plotly.graph_objects as go

def config_parser(file='weather.ini'):
    parser = configparser.ConfigParser()
    parser.read(file)

    config_dict = {}

    for element in parser.sections():
        config_dict[element] = {}
        for name, value in parser.items(element):
            config_dict[element][name] = value

    return config_dict

weather_dict = config_parser('weather.ini')
energy_dict = config_parser('energy.ini')

# print(type(energy_dict['utility']['id']))
# print(get_reading_for_days(id=energy_dict['hostel']['id'], key=energy_dict['hostel']['read_api_key'], num_days=1))

with st.status("Loading latest values:"):
    current_weather_data = get_current_data(api_key=weather_dict['cce-plaksha']['apikeyv2'], api_secret=weather_dict['cce-plaksha']['apisecret'], items = ["temp", "aqi_val", "hum", "wind_speed_last", "solar_rad"])
    energy_usage_in_last_24_hrs = get_reading_for_days(id=energy_dict['hostel']['id'], key=energy_dict['hostel']['read_api_key'], num_days=1)

print(current_weather_data)
# Placeholder values for the metrics
temperature = current_weather_data["temp"]
aqi = current_weather_data["aqi_val"]
humidity = current_weather_data["hum"]
wind_speed = current_weather_data["wind_speed_last"]
solar_radiation = current_weather_data["solar_rad"]

print(energy_usage_in_last_24_hrs)

energy_reading = energy_usage_in_last_24_hrs['field1'].astype(float)
energy_usage = energy_reading[len(energy_reading) - 1] - energy_reading[0]

st.session_state['temp'] = temperature
st.session_state['hum'] = humidity
st.session_state['aqi'] = aqi
st.session_state['wind_speed'] = wind_speed
st.session_state['solar'] = solar_radiation
st.session_state['energy_usage'] = energy_usage

# Start of the Streamlit layout
st.title('Know your campus!')

# Display the metrics
st.header("How's the environment?")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Temperature", f"{temperature} °C")
col2.metric("AQI", aqi)
col3.metric("Humidity", f"{humidity} %")
col4.metric("Wind (km/h)", wind_speed)
col5.metric("Solar Radiation", f"{solar_radiation}")

# Display what we do
st.header('Our resource usage')
col1, col2 = st.columns(2)
col1.metric("Energy Usage (last 24 hrs)", f"{energy_usage:.2f} kWh")

#! Insights with a chart ! problem detected
st.header('Insights')
with st.status("Loading this week's data"):
    three_day_weather_data = get_df_for_timeperiod(api_key=weather_dict['cce-plaksha']['apikeyv2'], api_secret=weather_dict['cce-plaksha']['apisecret'], period=24)
    three_day_energy_data = get_reading_for_days(id=energy_dict['hostel']['id'], key=energy_dict['hostel']['read_api_key'], num_days=1)

three_day_weather_data.index = pd.to_datetime(three_day_weather_data.index)
three_day_energy_data['created_at'] = pd.to_datetime(three_day_energy_data['created_at'])
three_day_energy_data['field1'] = three_day_energy_data['field1'].astype(float)#.diff().fillna(0)
three_day_energy_data['field1'] = three_day_energy_data['field1'].rolling(window=15).mean().fillna(0)

# Initialize an empty figure using go.Figure() instead of px.figure()
fig = go.Figure()

# Add the first scatter plot for weather data
# Note: We use fig.add_trace() instead of fig.add_scatter()
fig.add_trace(go.Scatter(
    x=three_day_weather_data.index, 
    y=three_day_weather_data['temp_avg'], # Assuming 'temp_avg' is a column in three_day_weather_data
    mode='markers', 
    name='Temperature Avg'
))
fig.add_trace(go.Scatter(
    x=three_day_weather_data.index, 
    y=three_day_weather_data['hum_last'], # Assuming 'hum_last' is a column in three_day_weather_data
    mode='markers', 
    name='Humidity Last'
))
fig.add_trace(go.Scatter(
    x=three_day_weather_data.index, 
    y=three_day_weather_data['solar_energy'], # Assuming 'solar_energy' is a column in three_day_weather_data
    mode='markers', 
    name='Solar Energy'
))

fig.add_trace(go.Scatter(
    x=three_day_energy_data['created_at'], 
    y=three_day_energy_data['field1'], 
    mode='lines', 
    name='Energy Reading', 
    yaxis='y2'
))

fig.update_layout(
    yaxis=dict(title='Weather Data'),
    yaxis2=dict(title='Energy Reading', overlaying='y', side='right'),
    title='Weather and Energy Data',
    legend=dict(x=1.10)
)

fig.update_xaxes(
    title_text='Time',
    rangeslider_visible=False,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1d", step="day", stepmode="backward"),
            dict(count=7, label="1w", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    ),
    type="date",
    tickformat="%H:%M",
    ticklabelmode="period",
)

st.plotly_chart(fig)

print(st.session_state)
time.sleep(5*60)

st.rerun()

