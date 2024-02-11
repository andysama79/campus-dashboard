import pandas as pd
import requests
from datetime import datetime, timedelta, UTC

# Set the channel ID and Read API Key for your ThingSpeak channel
channel_id = "2238279"
read_api_key = "KGYJDUYY76CKMC28"

def get_last_n_readings(n=1):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_api_key}&results={n}"

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

def get_reading_for_days(num_days=7):
    # Calculate the date num days ago from today
    num_days_ago = datetime.now(UTC) - timedelta(days=num_days)
    start_date = num_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')  # Format the date as required by the API

    # ThingSpeak API URL for retrieving the channel feed for the last 7 days
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_api_key}&start={start_date}"

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

if __name__ == "__main__":
    last_day_reading = get_reading_for_days(num_days=1)
