import solara as sol
import pdb
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from campusutils.campusweather import get_current_data, get_df_for_timeperiod
from campusutils.campusenergy import get_last_n_readings, get_reading_for_days

# Define reactive variables
temperature, aqi, humidity, wind_speed, solar_radiation, energy_usage = sol.reactive(None), sol.reactive(None), sol.reactive(None), sol.reactive(None), sol.reactive(None), sol.reactive(None)

#def update_dashboard():
#    current_weather_data = get_current_data(items=["temp", "aqi_val", "hum", "wind_speed_last", "solar_rad"])
#    
#    # Update the reactive variables
#    temperature.set(current_weather_data["temp"])
#    aqi.set(current_weather_data["aqi_val"])
#    humidity.set(current_weather_data["hum"])
#    wind_speed.set(current_weather_data["wind_speed_last"])
#    solar_radiation.set(current_weather_data["solar_rad"])
#
#    energy_usage_in_last_24_hrs = get_reading_for_days(num_days=1)
#    energy_reading = energy_usage_in_last_24_hrs['field1'].astype(float)
#    energy_usage.set(energy_reading[len(energy_reading) - 1] - energy_reading[0])

@sol.component
def MetricCard(label, value, unit=""):
    with sol.Card():
        with sol.VBox():
            sol.Markdown(f"**{label}**")
            sol.Markdown(f"# {value} {unit}")

def update_dashboard_once():
    current_weather_data = get_current_data(items=["temp", "aqi_val", "hum", "wind_speed_last", "solar_rad"])
    
    # Calculate energy usage
    energy_usage_in_last_24_hrs = get_reading_for_days(num_days=1)
    energy_reading = energy_usage_in_last_24_hrs['field1'].astype(float)
    energy_consumption = energy_reading[len(energy_reading) - 1] - energy_reading[0]

    # Yield the new data
    return {
        "temperature": current_weather_data["temp"],
        "aqi": current_weather_data["aqi_val"],
        "humidity": current_weather_data["hum"],
        "wind_speed": current_weather_data["wind_speed_last"],
        "solar_radiation": current_weather_data["solar_rad"],
        "energy_usage": energy_consumption
    }

def update_dashboard():
    while True:
        current_weather_data = get_current_data(items=["temp", "aqi_val", "hum", "wind_speed_last", "solar_rad"])
        
        # Calculate energy usage
        energy_usage_in_last_24_hrs = get_reading_for_days(num_days=1)
        energy_reading = energy_usage_in_last_24_hrs['field1'].astype(float)
        energy_consumption = energy_reading[len(energy_reading) - 1] - energy_reading[0]

        # Yield the new data
        yield {
            "temperature": current_weather_data["temp"],
            "aqi": current_weather_data["aqi_val"],
            "humidity": current_weather_data["hum"],
            "wind_speed": current_weather_data["wind_speed_last"],
            "solar_radiation": current_weather_data["solar_rad"],
            "energy_usage": energy_consumption
        }

        time.sleep(1)

def handle_refresh():
    data = update_dashboard_once()
    # Update the reactive variables
    temperature.set(data["temperature"])
    aqi.set(data["aqi"])
    humidity.set(data["humidity"])
    wind_speed.set(data["wind_speed"])
    solar_radiation.set(data["solar_radiation"])
    energy_usage.set(data["energy_usage"])

# Display the metrics and insights in Solara
@sol.component
def Page():
    with sol.Column():
        # Display the metrics
        with sol.VBox():
            sol.Button("Refresh Data", on_click=handle_refresh)
            sol.Markdown('### How\'s the environment?')
            with sol.HBox():
                MetricCard("Temperature", temperature.get(), "°C")
                MetricCard("AQI", aqi.get(), "")
                MetricCard("Humidity", humidity.get(), "%")
                MetricCard("Wind", wind_speed.get(), "kmph")
                MetricCard("Solar Radiation", solar_radiation.get(), "")
    
            # Display resource usage
            sol.Markdown('### Our resource usage')
            with sol.HBox():
                MetricCard("Energy Usage (last 24 hrs)", f"{energy_usage.get()} kWh")
            
            # Insights with a chart
            sol.Markdown('### Insights')
    
            # Explanatory text
            sol.Text('This week the energy usage went up/down by X%')
            sol.Text('This week it was X degrees cooler than last week')
            sol.Text('The breeze went to a max of 123 kmph last week')
            sol.Text('Visit mycampus.plaksha.edu.in for real-time data!')
