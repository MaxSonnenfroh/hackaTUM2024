from abc import ABC, abstractmethod
from scenario import Scenario, RoutingPlan, create_scenario, run_scenario, delete_scenarios

import numpy as np

class RoutingSolver(ABC):
    @abstractmethod
    def __call__(self, scenario: Scenario) -> RoutingPlan:
        pass

class ShortestJobFirst(RoutingSolver):
    def __call__(self, scenario: Scenario) -> RoutingPlan:
        v_pos = scenario.vehicle_positions
        c_pos = scenario.customer_positions

        # boolean mask for waiting customers
        c_waiting = np.ones(c_pos.shape[0], dtype=np.bool)

        # calculate squared distance for every pair
        dist = np.square(v_pos[:, None] - c_pos[None]).sum(axis=-1)
        solution = {}

        for _ in range(c_waiting.shape[0]):
            dist[:, ~c_waiting] = np.inf
            min_index = np.unravel_index(np.argmin(dist), dist.shape)

            v_id = str(scenario.vehicle_ids[min_index[0]])
            c_id = str(scenario.customers_ids[min_index[1]])
            c_waiting[min_index[1]] = False

            if v_id in solution:
                solution[v_id].append(c_id)
            else:
                solution[v_id] = [c_id]

            # recalculate distance as the vehicle position updated (now at customer)
            dist[min_index[0]] = np.square(c_pos[min_index[1]][None] - c_pos).sum(axis=-1)

        return RoutingPlan(
            scenario,
            solution,
        )

delete_scenarios() 
sjf = ShortestJobFirst()
scenario = create_scenario(num_vehicles=10, num_customers=10, speed=0.05)
plan = sjf(scenario)

mapping = plan.mapping
for key in mapping.keys():
    print(key, mapping[key])

print("=" * 50)
run_scenario(plan)