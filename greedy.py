import math

def assign_vehicles_to_customers(vehicles, customers):
    assignments = []
    for customer in customers:
        closest_vehicle = None
        min_distance = float('inf')
        for vehicle in vehicles:
            if vehicle['isAvailable']:
                distance = math.sqrt((vehicle['coordX'] - customer['coordX'])**2 + 
                                     (vehicle['coordY'] - customer['coordY'])**2)
                if distance < min_distance:
                    closest_vehicle = vehicle
                    min_distance = distance
        if closest_vehicle:
            assignments.append({'vehicle_id': closest_vehicle['id'], 'customer_id': customer['id']})
            closest_vehicle['isAvailable'] = False  # Mark the vehicle as assigned
    return assignments
