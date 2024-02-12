import pandas as pd
import datetime
import time
import tzlocal
import matplotlib.pyplot as plt

import hashlib
import hmac
import time
import urllib.request
import json

APIKeyv2 = "aqfzuj9ub5iodlrdwvhy0rvqb0ce62sd"
APISecret = "aujta0m5z2qiczvoxu49vc8umumkn2ac"

# get station id
print("-"*50)
print("\n\nStation ID")
t = int(time.time())

message_to_hash = "api-key{}t{}"\
                      .format(APIKeyv2, t)

apiSignature = hmac.new(
    APISecret.encode('utf-8'),
    message_to_hash.encode('utf-8'),
    hashlib.sha256
).hexdigest()

stations_url = "https://api.weatherlink.com/v2/stations?api-key={}&t={}&api-signature={}"\
                .format(APIKeyv2, t, apiSignature)
#print(stations_url,'\n')

with urllib.request.urlopen(stations_url) as url:
    data = json.loads(url.read().decode())
    #print(json.dumps(data, indent=4, sort_keys=False))

# in my case, there is only one station
# modifications are required if more than one
station_id   = data['stations'][0]['station_id']
station_name = data['stations'][0]['station_name']

print("Station ID: ", station_id)
print("Station_name: ", station_name)

# current data
print("-"*50)
print("\n\nCurrent data")
message_to_hash = "api-key{}station-id{}t{}"\
                      .format(APIKeyv2, station_id, t)

apiSignature = hmac.new(
      APISecret.encode('utf-8'),
      message_to_hash.encode('utf-8'),
      hashlib.sha256
    ).hexdigest()

current_url = "https://api.weatherlink.com/v2/current/{}?api-key={}&t={}&api-signature={}"\
                  .format(station_id, APIKeyv2, t, apiSignature)

with urllib.request.urlopen(current_url) as url:
    data = json.loads(url.read().decode())
    # print(json.dumps(data, indent=4, sort_keys=False))

# historic data
print("-"*50)
print("\n\nHistoric data")
period = 24
end_timestamp   = int(time.time())
start_timestamp = end_timestamp - period*3600 # maximum: 24 hours
message_to_hash = "api-key{}end-timestamp{}start-timestamp{}station-id{}t{}"\
                    .format(APIKeyv2, end_timestamp, start_timestamp, station_id, t)
apiSignature = hmac.new(
    APISecret.encode('utf-8'),
    message_to_hash.encode('utf-8'),
    hashlib.sha256
    ).hexdigest()

historic_url = "https://api.weatherlink.com/v2/historic/{}?api-key={}&t={}&start-timestamp={}&end-timestamp={}&api-signature={}"\
                .format(station_id, APIKeyv2, t, start_timestamp, end_timestamp, apiSignature)

with urllib.request.urlopen(historic_url) as url:
    data = json.loads(url.read().decode())
    print(json.dumps(data, indent=4, sort_keys=False))