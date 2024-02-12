import pandas as pd
import requests
import configparser
from datetime import datetime, timedelta, UTC

# parse the configuration file for channel ids and read api keys
def config_parser(file='energy.ini'):
    parser = configparser.ConfigParser()
    parser.read(file)

    config_dict = {}

    for element in parser.sections():
        config_dict[element] = {}
        for name, value in parser.items(element):
            config_dict[element][name] = value

    return config_dict

def get_last_n_readings(id, key, n=1):
    url = f"https://api.thingspeak.com/channels/{id}/feeds.json?api_key={key}&results={n}"

    # make GET request to the ThingSpeak API
    response = requests.get(url)
    response.raise_for_status()

    # load the response data into a pandas dataframe
    data = response.json()
    feeds = data['feeds']

    df = pd.DataFrame(feeds)

    return df

def get_reading_for_days(id, key, num_days=7):
    # Calculate the date num days ago from today
    num_days_ago = datetime.now(UTC) - timedelta(days=num_days)
    start_date = num_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')  # Format the date as required by the API

    # ThingSpeak API URL for retrieving the channel feed for the last 7 days
    url = f"https://api.thingspeak.com/channels/{id}/feeds.json?api_key={key}&start={start_date}"

    # Make a GET request to the ThingSpeak API
    response = requests.get(url)
    response.raise_for_status()  # This will raise an error if the request fails

    # Load the response data into a pandas DataFrame
    data = response.json()
    feeds = data['feeds']

    # Create a pandas DataFrame from the feeds
    df = pd.DataFrame(feeds)

    # Display the DataFrame
    return df

def main():
    config_dict = config_parser()
    print(config_dict)
    print(get_last_n_readings(id=config_dict['utility']['id'], key=config_dict['utility']['read_api_key']))
    print(get_reading_for_days(id=config_dict['utility']['id'], key=config_dict['utility']['read_api_key']))

if __name__ == "__main__":
    main()