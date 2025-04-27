from flask import Flask, request, jsonify, render_template
import numpy as np
import csv
import os
from aco import AntColony

app = Flask(__name__)

# CSV'den şehir verilerini yükleme fonksiyonu
def load_cities_from_csv(filename: str) -> list[dict]:
    """
    id, name, x, y alanlarına sahip sözlüklerin listesi olarak şehirleri döndürür.
    """
    cities: list[dict] = []
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

# Uygulama başlatıldığında şehirleri yükleyelim
CITIES = load_cities_from_csv('cities.csv')

@app.route('/')
def index() -> str:
    """Ana sayfa: Harita ve kontrol arayüzü"""
    return render_template('index.html')

@app.route('/locations')
def get_locations():
    """Tüm şehirleri JSON olarak döndürür"""
    return jsonify(CITIES)

@app.route('/run_aco', methods=['POST'])
def run_aco():
    """Gönderilen parametrelere göre ACO çalıştırır ve en iyi rotayı döner"""
    data = request.get_json()
    start_id = data.get('start')
    dest_ids = data.get('destinations', [])
    n_ants = data.get('nAnts', 10)
    n_iters = data.get('nIters', 50)
    alpha = data.get('alpha', 1.0)
    beta = data.get('beta', 3.0)
    rho = data.get('rho', 0.5)

    # Başlangıç + hedefleri birleştir ve tekrarları kaldır
    unique_ids = [start_id] + dest_ids
    unique_ids = list(dict.fromkeys(unique_ids))

    # ID -> (x, y) sözlüğü
    city_map = {c['id']: (c['x'], c['y']) for c in CITIES}
    coords = [city_map[cid] for cid in unique_ids]

    # ACO için mesafe matrisi
    dist_matrix = create_distance_matrix(coords)

    # ACO nesnesi
    ac = AntColony(
        distance_matrix=dist_matrix,
        n_ants=n_ants,
        n_iterations=n_iters,
        alpha=alpha,
        beta=beta,
        evaporation_rate=rho
    )
    best_route, best_distance = ac.run()

    # Global ID ve isim listelerine dönüştür
    best_global_ids = [unique_ids[i] for i in best_route]
    best_names = [next(c['name'] for c in CITIES if c['id'] == cid) for cid in best_global_ids]

    return jsonify({
        'bestRouteGlobalIds': best_global_ids,
        'bestPathNames': best_names,
        'bestLength': best_distance
    })

def create_distance_matrix(coords: list[tuple[float, float]]) -> np.ndarray:
    """
    Öklidyen mesafe matrisini döndürür.
    coords: [(x1,y1), (x2,y2), ...]
    """
    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i, j] = np.linalg.norm(np.array(coords[i]) - np.array(coords[j]))
    return matrix

if __name__ == '__main__':
    app.run(debug=True)
