import json
from collections import defaultdict

def load_geojson():
    with open('bhubaneswar_traffic_flow.geojson') as f:
        return json.load(f)

def extract_road_segments(geojson):
    roads = []
    for feature in geojson['features']:
