import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import distance

# Beispiel-Daten: Fahrzeuge und Kunden
vehicles = [{'id': f'v{i}', 'coordX': 0, 'coordY': 0} for i in range(5)]  # 5 Fahrzeuge am Ursprung
customers = [{'id': f'c{i}', 'coordX': np.random.uniform(0, 100), 'coordY': np.random.uniform(0, 100)} for i in range(20)]  # 20 zufällige Kunden

# Funktion: Cluster-First
def cluster_customers(customers, n_vehicles):
    coords = np.array([[c['coordX'], c['coordY']] for c in customers])
    kmeans = KMeans(n_clusters=n_vehicles, random_state=42).fit(coords)
    clusters = {i: [] for i in range(n_vehicles)}
    for i, label in enumerate(kmeans.labels_):
        clusters[label].append(customers[i])
    return clusters

# Funktion: Route-Second (Greedy)
def greedy_route(cluster, start_point):
    route = []
    remaining = cluster[:]
    current_point = start_point
    
    while remaining:
        # Finde den nächsten Kunden (kleinste Distanz)
        next_customer = min(remaining, key=lambda c: distance.euclidean(
            (current_point['coordX'], current_point['coordY']),
            (c['coordX'], c['coordY'])
        ))
        route.append(next_customer)
        current_point = next_customer
        remaining.remove(next_customer)
    
    return route

# Haupt-Programm
def solve_vrp(vehicles, customers):
    # Schritt 1: Cluster-First (Kunden auf Fahrzeuge aufteilen)
    clusters = cluster_customers(customers, len(vehicles))
    
    # Schritt 2: Route-Second (Route für jedes Fahrzeug berechnen)
    routes = {}
    for vehicle_id, (vehicle, cluster) in enumerate(zip(vehicles, clusters.values())):
        start_point = {'coordX': vehicle['coordX'], 'coordY': vehicle['coordY']}
        routes[vehicle['id']] = greedy_route(cluster, start_point)
    
    return routes

# Lösen des VRP
routes = solve_vrp(vehicles, customers)

# Ergebnis ausgeben
for vehicle_id, route in routes.items():
    print(f"Fahrzeug {vehicle_id} Route:")
    for stop in route:
        print(f"  - Kunde {stop['id']} @ ({stop['coordX']:.2f}, {stop['coordY']:.2f})")
