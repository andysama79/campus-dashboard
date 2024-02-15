import pandas as pd
import datetime
import configparser
import time
import tzlocal
import matplotlib.pyplot as plt

import hashlib
import hmac
import time
import urllib.request
import json
# import streamlit as st

def config_parser(file='weather.ini'):
    parser = configparser.ConfigParser()
    parser.read(file)

    config_dict = {}

    for element in parser.sections():
        config_dict[element] = {}
        for name, value in parser.items(element):
            config_dict[element][name] = value

    return config_dict

def get_station_id(api_key, api_secret, t):
    message_to_hash = "api-key{}t{}"\
                      .format(api_key, t)

    apiSignature = hmac.new(
      api_secret.encode('utf-8'),
      message_to_hash.encode('utf-8'),
      hashlib.sha256
    ).hexdigest()

    stations_url = "https://api.weatherlink.com/v2/stations?api-key={}&t={}&api-signature={}"\
                   .format(api_key, t, apiSignature)
    #print(stations_url,'\n')

    with urllib.request.urlopen(stations_url) as url:
        data = json.loads(url.read().decode())
        #print(json.dumps(data, indent=4, sort_keys=False))

    # in my case, there is only one station
    # modifications are required if more than one
    station_id   = data['stations'][0]['station_id']
    station_name = data['stations'][0]['station_name']
    #print("\nstation_id:   {}\nstation_name: {}".format(station_id,station_name))

    return station_id, station_name

def get_current_data(api_key, api_secret, items=["hum","temp","aqi_val","pm_1","pm_2p5","pm_10","aqi_nowcast_val", "wind_speed_last"]):
    """Receives a list of items as arguments and returns a dict containing current values """

    current_items = items
    t = int(time.time())
    station_id, station_name = get_station_id(api_key, api_secret, t)

    ## --------------------------------
    ## Read the current conditions data
    ## --------------------------------

    t               = int(time.time())
    message_to_hash = "api-key{}station-id{}t{}"\
                      .format(api_key, station_id, t)
    #print(message_to_hash)

    apiSignature = hmac.new(
      api_secret.encode('utf-8'),
      message_to_hash.encode('utf-8'),
      hashlib.sha256
    ).hexdigest()

    current_url = "https://api.weatherlink.com/v2/current/{}?api-key={}&t={}&api-signature={}"\
                  .format(station_id, api_key, t, apiSignature)

    with urllib.request.urlopen(current_url) as url:
        data = json.loads(url.read().decode())
        #print(json.dumps(data, indent=4, sort_keys=True))


    item_data = {}
    for sensor in data['sensors']:
        current_data = sensor['data'][0]
        for item in current_items:
            if item in current_data:
                item_data[item] = int(current_data[item])

    #Converting to celsius
    item_data['temp'] = int((item_data['temp'] - 32) * 5.0/9.0)

    df = pd.DataFrame(data=item_data,index=[pd.Timestamp(datetime.datetime.today())])

    return df[current_items].to_dict('records')[0]

def get_df_for_timeperiod(api_key, api_secret, period=24, items=["wind_speed_hi", "temp_avg", "temp_lo", "temp_hi", "hum_last", "solar_energy", "temp_hi_at", "temp_lo_at"]):
    """Returns a dataframe containing values for 'period' hours."""

    current_items = items

    end_timestamp   = int(time.time())
    start_timestamp = end_timestamp - period*60*60 # maximum: 24 hours

    t               = int(time.time())
    station_id, station_name = get_station_id(api_key, api_secret, t)
    # historic data
    message_to_hash = "api-key{}end-timestamp{}start-timestamp{}station-id{}t{}"\
                    .format(api_key, end_timestamp, start_timestamp, station_id, t)
    #print(message_to_hash)

    apiSignature = hmac.new(
    api_secret.encode('utf-8'),
    message_to_hash.encode('utf-8'),
    hashlib.sha256
    ).hexdigest()
    #print(apiSignature)

    historic_url = "https://api.weatherlink.com/v2/historic/{}?api-key={}&t={}&start-timestamp={}&end-timestamp={}&api-signature={}"\
                .format(station_id, api_key, t, start_timestamp, end_timestamp, apiSignature)
    #print(historic_url,'\n')

    with urllib.request.urlopen(historic_url) as url:
        data = json.loads(url.read().decode())

    df_list = [pd.DataFrame(data=sensor['data']) for sensor in data['sensors']]

    df = pd.concat(df_list, ignore_index=True)

    # convert temperature values to celsius
    df['temp_avg'] = (df['temp_avg'] - 32) * 5.0/9.0
    df['temp_lo'] = (df['temp_lo'] - 32) * 5.0/9.0
    df['temp_hi'] = (df['temp_hi'] - 32) * 5.0/9.0

    local_timezone = tzlocal.get_localzone()
    df['date'] = pd.to_datetime(df.ts, unit='s', utc=True).dt.tz_convert(local_timezone).dt.tz_localize(None)
    df.replace('', pd.NA)
    # df.dropna(inplace=True)
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    df = df.loc[:, current_items]
    # df.to_csv("records.csv")
    return df

def main():
    config_dict = config_parser()
    print(config_dict)
    print(get_current_data(api_key=config_dict['cce-plaksha']['apikeyv2'], api_secret=config_dict['cce-plaksha']['apisecret']))
    df = get_df_for_timeperiod(api_key=config_dict['cce-plaksha']['apikeyv2'], api_secret=config_dict['cce-plaksha']['apisecret'], period=48)
    print(df)

if __name__ == "__main__":
    main()