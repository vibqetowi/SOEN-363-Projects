from gdacs.api import GDACSAPIReader
import json

client = GDACSAPIReader()

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
        "latitude": geometry.get("coordinates", [0,0])[0],
        "longitude": geometry.get("coordinates", [0,0])[1],
        "depth": depth,
        "magnitude": magnitude,
        "event_type": properties.get("eventtype", "N/A"),
    }
    events.append(event)

for event in events:
    print(json.dumps(event, indent=2))
