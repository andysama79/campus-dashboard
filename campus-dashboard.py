import streamlit as st
import pdb
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from campusutils.campusweather import get_current_data, get_df_for_timeperiod
from campusutils.campusenergy import get_last_n_readings, get_reading_for_days
import plotly.express as px
import plotly.graph_objects as go

with st.status("Loading latest values:"):
    current_weather_data = get_current_data(items = ["temp", "aqi_val", "hum", "wind_speed_last", "solar_rad"])
    energy_usage_in_last_24_hrs = get_reading_for_days(num_days=1)

print(current_weather_data)
# Placeholder values for the metrics
temperature = current_weather_data["temp"]
aqi = current_weather_data["aqi_val"]
humidity = current_weather_data["hum"]
wind_speed = current_weather_data["wind_speed_last"]
solar_radiation = current_weather_data["solar_rad"]

#current_meter_reading = get_last_n_readings(n=1)
#energy_usage = float(current_meter_reading.loc[0, ['field1']])

energy_reading = energy_usage_in_last_24_hrs['field1'].astype(float)
energy_usage = energy_reading[len(energy_reading) - 1] - energy_reading[0]
water_usage = 500

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
col1.metric("Energy Usage (last 24 hrs)", f"{energy_usage} kWh")
#col2.metric("Water Usage", f"{water_usage} L")

# Insights with a chart
st.header('Insights')
with st.status("Loading this week's data"):
    three_day_weather_data = get_df_for_timeperiod(period=24)
    three_day_energy_data = get_reading_for_days(num_days=1)

three_day_weather_data.index = pd.to_datetime(three_day_weather_data.index)
three_day_energy_data['created_at'] = pd.to_datetime(three_day_energy_data['created_at'])
three_day_energy_data['field1'] = three_day_energy_data['field1'].astype(float)
three_day_energy_data['field1'] = three_day_energy_data['field1'].rolling(window=5).mean().fillna(0)

#three_day_energy_data['field1'] -= three_day_energy_data['field1'].min()

#three_day_energy_data['field1'] =  [0] + [three_day_energy_data[x] - three_day_energy_data[x-1] for x in range(1, len(three_day_energy_data) - 1)]

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

# Change the second scatter plot for energy data to a line plot
# Note: Assigning it to the secondary y-axis 'yaxis2'
fig.add_trace(go.Scatter(
    x=three_day_energy_data['created_at'], 
    y=three_day_energy_data['field1'], 
    mode='lines', 
    name='Energy Reading', 
    yaxis='y2'
))

# Update layout for the y-axes
fig.update_layout(
    yaxis=dict(title='Weather Data'),
    yaxis2=dict(title='Energy Reading', overlaying='y', side='right'),
    title='Weather and Energy Data'
)

#fig = px.figure()
#fig.add_scatter(three_day_weather_data, x=three_day_weather_data.index, y=['temp_avg', 'hum_last','solar_energy'], mode='markers', labels={'value': 'Value', 'date': 'Date'}, name='Weather Data')
#fig.add_scatter(x=three_day_energy_data['created_at'], y=three_day_energy_data['field1'], mode='markers', name='Energy Reading', yaxis='y2')
#fig.update_layout(
#    yaxis=dict(title='Weather Data'),
#    yaxis2=dict(title='Energy Reading', side='right'))
##fig.update_traces(hovertemplate='Value: %{y}<extra></extra>')

st.plotly_chart(fig)
## Explanatory text
#st.text('This week the energy usage went up/down by X%')
#st.text('This week it was X degrees cooler than last week')
#st.text('The breeze went to a max of 123 kmph last week')
#st.text('Visit mycampus.plaksha.edu.in for real-time data!')

# To run the Streamlit app, save this script as `app.py` and
# use the command `streamlit run app.py` in your terminal.
while True:
    current_weather_data = get_current_data(items = ["temp", "aqi_val", "hum", "wind_speed_last", "solar_rad"])
    #print(current_weather_data)
    # Placeholder values for the metrics
    temperature = current_weather_data["temp"]
    aqi = current_weather_data["aqi_val"]
    humidity = current_weather_data["hum"]
    wind_speed = current_weather_data["wind_speed_last"]
    solar_radiation = current_weather_data["solar_rad"]

    energy_usage_in_last_24_hrs = get_reading_for_days(num_days=1)
    energy_reading = energy_usage_in_last_24_hrs['field1'].astype(float)
    energy_usage = energy_reading[len(energy_reading) - 1] - energy_reading[0]

    st.session_state['temp'] = temperature
    st.session_state['hum'] = humidity
    st.session_state['aqi'] = aqi
    st.session_state['wind_speed'] = wind_speed
    st.session_state['solar'] = solar_radiation
    st.session_state['energy_usage'] = energy_usage

    print(st.session_state)
    time.sleep(1 * 60 * 1000)
    st.rerun()

