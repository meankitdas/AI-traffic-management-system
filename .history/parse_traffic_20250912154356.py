import json
from collections import defaultdict

def load_geojson():
    with open('bhubaneswar_traffic_flow.geojson') as f:
        return json.load(f)

def extract_road_segments(geojson):
    roads = []
    for feature in geojson['features']:
        if (feature['geometry']['type'] == 'LineString' and
            'road_id' in feature['properties'] and
            'avg_speed_kmph' in feature['properties'] and
            'congestion' in feature['properties']):
            props = feature['properties']
            road = {
                'id': props['road_id'],
                'geometry': feature['geometry']['coordinates'],
                'avg_speed_kmph': props['avg_speed_kmph'],
                'congestion': props['congestion'],
                'vehicle_count': props['vehicle_count'] if 'vehicle_count' in props else 0,
                'travel_time_sec': props['travel_time_sec'] if 'travel_time_sec' in props else 0
            }
            roads.append(road)
    return roads

def build_graph(roads):
    point_to_roads = defaultdict(list)
    all_edges = []
    graph = defaultdict(list)

    def round_point(coord):
        return (round(coord[0], 5), round(coord[1], 5))  # lng, lat

    for road in roads:
        coords = road['geometry']
        road_id = road['id']
        rounded_coords = [round_point(c) for c in coords]

        # Add to point_to_roads for intersection detection
        for i, p in enumerate(rounded_coords):
            point_to_roads[p].append({
                'road_id': road_id,
                'index': i,
                'properties': road
            })

        # Create edges
        for i in range(len(rounded_coords) - 1):
            p1 = rounded_coords[i]
            p2 = rounded_coords[i + 1]
            edge_data = {
                'road_id': road_id,
                'avg_speed_kmph': road['avg_speed_kmph'],
                'congestion': road['congestion'],
                'vehicle_count': road['vehicle_count'],
                'travel_time_sec': road['travel_time_sec'],
                'length': calculate_distance(coords[i], coords[i+1])  # approx distance
            }
            all_edges.append({
                'start': p1,
                'end': p2,
                'data': edge_data
            })
            graph[p1].append({'node': p2, 'data': edge_data})
            graph[p2].append({'node': p1, 'data': edge_data})

    return graph, all_edges, point_to_roads

def calculate_distance(p1, p2):
    import math
    # Simple Euclidean, not great for lat/lng, but for rough
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def detect_intersections(point_to_roads):
    intersections = {}
    for point, roads_at_point in point_to_roads.items():
        unique_roads = set(r['road_id'] for r in roads_at_point)
        if len(unique_roads) > 1 or any(r['index'] in [0, len(roads[0]['properties']['geometry'])//2 - 1] for r in roads_at_point):
            intersections[point] = roads_at_point
    return intersections

