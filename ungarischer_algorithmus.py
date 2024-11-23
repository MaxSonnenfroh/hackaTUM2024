import numpy as np
from scipy.optimize import linear_sum_assignment

def assign_vehicles_customers(vehicles, customers):
    n_vehicles = len(vehicles)
    n_customers = len(customers)
    
    # Kostenmatrix erstellen (Distanz zwischen Fahrzeugen und Kunden)
    cost_matrix = np.zeros((n_vehicles, n_customers))
    for i, vehicle in enumerate(vehicles):
        for j, customer in enumerate(customers):
            cost_matrix[i][j] = np.sqrt((vehicle['coordX'] - customer['coordX'])**2 + 
                                        (vehicle['coordY'] - customer['coordY'])**2)
    
    # Ungarischer Algorithmus anwenden
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # Ergebnis: Fahrzeug-Kunden-Zuweisung
    assignments = []
    for i, j in zip(row_ind, col_ind):
        assignments.append({'vehicle_id': vehicles[i]['id'], 'customer_id': customers[j]['id']})
    
    return assignments
