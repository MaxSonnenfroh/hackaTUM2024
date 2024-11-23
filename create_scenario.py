import requests

BACKEND_ENDPOINT = "http://localhost:8080"
RUNNER_ENDPOINT = "http://localhost:8090"

scenario_setting = {"numberOfVehicles": 5, "numberOfCustomers": 10}

scenario = requests.post(f"{BACKEND_ENDPOINT}/scenario/create", json=scenario_setting).json()

vehicles = scenario["vehicles"]
customers = scenario["customers"]
print(f"Scenario with ID {scenario['id']} was {scenario['status']}, it has {len(vehicles)} vehicles and {len(customers)} customers")

response = requests.post(f"{RUNNER_ENDPOINT}/Scenarios/initialize_scenario", json=scenario).json()
print(response["message"])

response = requests.post(f"{RUNNER_ENDPOINT}/Runner/launch_scenario/{scenario['id']}", json={"speed": 0.2, "scenario_id": scenario["id"]}).json()
print(response["message"])
print(f"\tlaunch time: {response['startTime']}")
