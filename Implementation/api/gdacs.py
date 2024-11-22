from gdacs.api import GDACSAPIReader
import json

client = GDACSAPIReader()
event_types = {
    "TC": "Tropical Cyclone",
    "EQ": "Earthquake",
    "FL": "Flood",
    "VO": "Volcano",
    "WF": "Wild Fire",
    "DR": "Drought",
    "N/A": "N/A"
}

def get_events():

    #events = client.latest_events() # all recent events
    data = client.latest_events(limit=20)
    events = []

    for feature in data.features:
        geometry = feature.get('geometry', {})
        properties = feature.get('properties', {})

        severity_text = properties.get("severitydata", {}).get("severitytext", "")
        magnitude = None
        depth = None
        if severity_text:
            try:
                parts = severity_text.split(", ")
                magnitude = float(parts[0].replace("Magnitude", "").replace("M", "").strip())
                depth = float(parts[1].replace("Depth:", "").replace("km", "").strip())
            except (IndexError, ValueError):
                print(f"Error parsing severity: {severity_text}")

        #filtered for only necessary fields
        event = {
            "time": properties.get("fromdate", "N/A"),
            "latitude": geometry.get("coordinates", [0,0])[1],
            "longitude": geometry.get("coordinates", [0,0])[0],
            "depth": depth,
            "magnitude": magnitude,
            "event_type": event_types.get(properties.get("eventtype", "N/A")).capitalize(),
        }
        events.append(event)

    return events
