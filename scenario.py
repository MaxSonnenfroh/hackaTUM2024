import requests
import numpy as np
import threading
import time

from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List

BACKEND_ENDPOINT = "http://localhost:8080"
RUNNER_ENDPOINT = "http://localhost:8090"
FRONTEND_ENDPOINT = "http://localhost:8000/send-message"

waitingCustomers = np.array([[1,22],[2,72],[3,48]])
customersInTransit = np.array([4,5])

@dataclass
class Scenario:
    scenario_id: str
    scenario_speed: float

    vehicle_ids: np.ndarray
    vehicle_positions: np.ndarray

    customers_ids: np.ndarray
    customer_src_positions: np.ndarray
    customer_dst_positions: np.ndarray

@dataclass
class RoutingPlan:
    scenario: Scenario

    # mapping from vehicle_id to List[customer_id]
    mapping: Dict[str, List[str]]

def initializeFrontend(scenario: Scenario):
    scenario_data = requests.get(f"{RUNNER_ENDPOINT}/Scenarios/get_scenario/{scenario.scenario_id}").json()
    vehicles = getStartingVehicles(scenario_data)
    customers = getStartingCustomers(scenario_data)
    return {
        "key": "init",
        "value": {
            "vehicles": vehicles,
            "customers": customers
        }
    }

def getStartingVehicles(scenario):
    vehicles = [[vehicle['id'], [vehicle['coordX']], vehicle['coordY']] for vehicle in scenario['vehicles']]
    return vehicles

def getStartingCustomers(scenario):
    customers = [[customer['id'], [customer['coordX'], customer['coordY']], [customer['destinationX'], customer['destinationY']]] for customer in scenario['customers']]
    return customers

def getFrontendData(scenario: Scenario):
    scenario_data = requests.get(f"{RUNNER_ENDPOINT}/Scenarios/get_scenario/{scenario['id']}").json()
    totalTime = computeTotalTime(scenario_data)
    waitingTime = computeWaitingTime(scenario_data)
    averageWaitingTime = (np.array(waitingTime)[:, 1]).astype(int).mean()
    activeTimes = computeActiveTime(scenario_data)
    averageUtilization = (np.array(activeTimes)[:, 1]).astype(int).mean()
    loadBigger75 = [[vehicle, activeTime] for vehicle, activeTime in activeTimes if activeTime > 0.75 * totalTime.total_seconds()]
    loadSmaler25 = [[vehicle, activeTime] for vehicle, activeTime in activeTimes if activeTime < 0.25 * totalTime.total_seconds()]
    waitingCustomers = computeWaitingTime(scenario_data)
    extremeWaitTime = [[customer[0], customer[1]] for customer in waitingCustomers if customer[1] > 10 * 60]
    customersInTransit = computeCustomerInTransit(scenario_data)
    droppedCustomers = computeDroppedCustomers(scenario_data)
    currentDistance = computeCurrentDistance(scenario_data)
    
    return {
            "key": "update",
            "value": {
                "totalTime": str(totalTime),
                "averageWait": averageWaitingTime,
                "averageUtilization": averageUtilization,
                "loadBigger75": loadBigger75,
                "loadSmaler25": loadSmaler25,
                "extremeWaitTime": extremeWaitTime,
                "waitingCustomers": waitingCustomers,
                "customersOnTransit": customersInTransit,
                "dropedCustomers": droppedCustomers,
                "currentDistance": currentDistance
            }
        }

def computeTotalTime(scenario):
    start_time = datetime.fromisoformat(scenario["startTime"])
    if scenario['status'] != 'COMPLETED':
        end_time = datetime.utcnow()
    else:
        end_time = datetime.fromisoformat(scenario["endTime"])
    totalTime = end_time - start_time
    return totalTime

def computeWaitingTime(scenario):
    if scenario['status'] == 'RUNNING':
        waitingCustomers1 = waitingCustomers
    else:
        waitingCustomers1 = scenario['customers']
    waitingTime = waitingCustomers1
    return np.array(waitingTime)

def computeActiveTime(scenario):
    return [[vehicle['id'], vehicle['activeTime']] for vehicle in scenario['vehicles']]


def computeWaitTime(scenario):
    customers = scenario['customers']

def computeDroppedCustomers(scenario):
    return [[vehicle['id'], vehicle['distanceTravelled']] for vehicle in scenario['vehicles']]

def computeCustomerInTransit(scenario):
    return customersInTransit


def computeCurrentDistance(scenario):
    return [[vehicle['id'], vehicle['distanceTravelled']] for vehicle in scenario['vehicles']]

def delete_scenarios():
    scenarios = requests.get(f"{BACKEND_ENDPOINT}/scenarios").json()
    for scenario in scenarios:
        requests.delete(f"{BACKEND_ENDPOINT}/scenarios/{scenario['id']}")

def create_scenario(num_vehicles=5, num_customers=10, speed=0.2):
    scenario = requests.post(
        f"{BACKEND_ENDPOINT}/scenario/create?numberOfVehicles={num_vehicles}&numberOfCustomers={num_customers}"
    ).json()
    
    vehicles = scenario["vehicles"]
    customers = scenario["customers"]
    print(f"Scenario with ID {scenario['id']} was {scenario['status']}, it has {len(vehicles)} vehicles and {len(customers)} customers")

    response = requests.post(f"{RUNNER_ENDPOINT}/Scenarios/initialize_scenario", json=scenario).json()
    print(response["message"])

    response = requests.post(
        f"{RUNNER_ENDPOINT}/Runner/launch_scenario/{scenario['id']}?speed={speed}"
    ).json()
    start_time = response["startTime"]
    scenario["startTime"] = start_time

    print(response["message"])
    print(f"\tstart time: {start_time}")

    vehicle_ids = np.array([vehicle["id"] for vehicle in vehicles])
    vehicle_positions = np.stack([
        np.array([vehicle["coordX"] for vehicle in vehicles]),
        np.array([vehicle["coordY"] for vehicle in vehicles]),
    ]).transpose()

    customers_ids = np.array([customer["id"] for customer in customers])
    customer_src_positions = np.stack([
        np.array([customer["coordX"] for customer in customers]),
        np.array([customer["coordY"] for customer in customers]),
    ]).transpose()

    customer_dest_positions = np.stack([
        np.array([customer["destinationX"] for customer in customers]),
        np.array([customer["destinationY"] for customer in customers]),
    ]).transpose()

    return Scenario(
        scenario["id"],
        speed,
        vehicle_ids,
        vehicle_positions,
        customers_ids,
        customer_src_positions,
        customer_dest_positions,
    )

def wait_for_vehicle(scenario: Scenario, vehicle_id: str):
    while True:
        response = requests.get(f"{RUNNER_ENDPOINT}/Scenarios/get_scenario/{scenario.scenario_id}").json()
        vehicle = [vehicle for vehicle in response["vehicles"] if vehicle["id"] == vehicle_id]

        if not vehicle:
            raise Exception("Vehicle does not exist")
    
        if vehicle[0]["customerId"] is not None:
            sleep_time = vehicle[0]["remainingTravelTime"] * scenario.scenario_speed
            print(f"Vehicle {vehicle_id} not finished; sleeping for {sleep_time}s")
            time.sleep(sleep_time + 1)
        else:
            break

def add_customer_to_vehicle(scenario: Scenario, vehicle_id: str, customer_id: str):
    mapping = {
        "vehicles": [{"id": vehicle_id, "customerId": customer_id,}]
    }

    response = requests.put(f"{RUNNER_ENDPOINT}/Scenarios/update_scenario/{scenario.scenario_id}", json=mapping).json()

    if "failedToUpdate" in response:
        raise Exception("Could not update vehicle")
    
    print(f"Vehicle {vehicle_id} driving to {customer_id}, estimated time: {response['updatedVehicles'][0]['remainingTravelTime'] * scenario.scenario_speed}")

def get_final_info(scenario: Scenario):
    response = requests.get(f"{RUNNER_ENDPOINT}/Scenarios/get_scenario/{scenario.scenario_id}").json()
    return (
        response["status"],
        datetime.fromisoformat(response["startTime"]),
        datetime.fromisoformat(response["endTime"]),
    )

def run_vehicle(routing_plan: RoutingPlan, vehicle_id: str):
    customers = routing_plan.mapping[vehicle_id]

    for customer_id in customers:
        add_customer_to_vehicle(routing_plan.scenario, vehicle_id, customer_id)
        wait_for_vehicle(routing_plan.scenario, vehicle_id)

def run_ui(scenario: Scenario):
    frontend_data = getFrontendData(scenario)
    response = requests.get(FRONTEND_ENDPOINT, json=frontend_data)
    assert response.status_code == 200
    time.sleep(1)

def run_scenario(routing_plan: RoutingPlan):
    threads = []
    initialize_data = initializeFrontend(routing_plan.scenario)
    response = requests.get(FRONTEND_ENDPOINT, json=initialize_data)
    assert response.status_code == 200

    for vehicle_id in routing_plan.mapping.keys():
        thread = threading.Thread(target=run_vehicle, args=(routing_plan, vehicle_id))
        thread.start()
        threads.append(thread)

    ui_thread = threading.Thread(target=run_ui, args=(routing_plan.scenario, ))
    ui_thread.start()
    threads.append(ui_thread)
    
    for thread in threads:
        thread.join()

    status, start, end = get_final_info(routing_plan.scenario)
    print(status, start, end)
