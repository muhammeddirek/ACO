from flask import Flask, request, jsonify, render_template
import numpy as np
import csv
import os
from aco import AntColony

app = Flask(__name__)

def load_cities_from_csv(filename: str) -> list[dict]:
    cities = []
    csv_path = os.path.join(os.path.dirname(__file__), filename)
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities.append({
                'id': int(row['id']),
                'name': row['name'],
                'x': float(row['x']),
                'y': float(row['y'])
            })
    return cities

CITIES = load_cities_from_csv('cities.csv')

def generate_all_edges(cities):
    edges = []
    city_ids = [city['id'] for city in cities]
    for i in range(len(city_ids)):
        for j in range(i+1, len(city_ids)):
            edges.append((city_ids[i], city_ids[j]))
    return edges

EDGES = generate_all_edges(CITIES)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/locations')
def get_locations():
    return jsonify(CITIES)

@app.route('/run_aco', methods=['POST'])
def run_aco():
    data = request.get_json()
    start_id = data.get('start')
    dest_ids = data.get('destinations', [])
    n_ants = data.get('nAnts', 10)
    n_iters = data.get('nIters', 50)
    alpha = data.get('alpha', 1.0)
    beta = data.get('beta', 3.0)
    rho = data.get('rho', 0.5)

    unique_ids = [start_id] + dest_ids
    unique_ids = list(dict.fromkeys(unique_ids))

    city_map = {c['id']: (c['x'], c['y']) for c in CITIES}
    coords = [city_map[cid] for cid in unique_ids]

    local_edges = [(unique_ids.index(f), unique_ids.index(t))
                   for f, t in EDGES if f in unique_ids and t in unique_ids]

    if not local_edges:
        return jsonify({'error': 'Seçilen şehirler arasında hiç yol tanımlı değil!'}), 400

    dist_matrix = create_distance_matrix(coords, local_edges)

    ac = AntColony(dist_matrix, n_ants, n_iters, alpha, beta, rho, start_city=0)
    best_route, best_distance = ac.run()

    best_global_ids = [unique_ids[i] for i in best_route]
    best_names = [next(c['name'] for c in CITIES if c['id'] == cid) for cid in best_global_ids]

    return jsonify({
        'bestRouteGlobalIds': best_global_ids,
        'bestPathNames': best_names,
        'bestLength': best_distance
    })

def create_distance_matrix(coords: list[tuple[float, float]], edges: list[tuple[int, int]]) -> np.ndarray:
    n = len(coords)
    matrix = np.full((n, n), np.inf)
    for from_idx, to_idx in edges:
        distance = np.linalg.norm(np.array(coords[from_idx]) - np.array(coords[to_idx]))
        matrix[from_idx, to_idx] = distance
        matrix[to_idx, from_idx] = distance
    return matrix

if __name__ == '__main__':
    app.run(debug=True)
