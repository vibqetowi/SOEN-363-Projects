import requests
import datetime


#Alternatively this is a link that downloads a csv
urlCSV = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2014-01-01&endtime=2014-01-02"

def formatTime(timestamp_ms):
    timestamp_s = timestamp_ms / 1000
    dt = datetime.datetime.utcfromtimestamp(timestamp_s)
    return dt.strftime('%Y-%m-%dT%H:%M:%S')

def get_events():

    urlGEOJSON = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2014-01-01&endtime=2014-01-02"
    response = requests.get(urlGEOJSON)
    geoJSON = response.json()

    events = []
    for feature in geoJSON.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        time = formatTime(properties.get("time", "N/A"))
        coordinates = geometry.get("coordinates", [0, 0, 0])
        latitude = coordinates[1]
        longitude = coordinates[0]
        depth = coordinates[2]
        magnitude = properties.get("mag", "N/A")
        event_type = properties.get("type", "N/A")

        #filtered for only necessary fields
        event = {
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "depth": depth,
            "magnitude": magnitude,
            "event_type": event_type,
        }

        events.append(event)

    return events
