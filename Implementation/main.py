from api import gdacs, usgs


if __name__ == '__main__':
    gdacs_events = gdacs.get_events()
    usgs_events = usgs.get_events()

