import simpy
import random
import statistics


# Simulation Parameters
RANDOM_SEED = 42
SIM_TIME = 120  # total simulation time (minutes)

# initialize
ARRIVAL_INTERVAL = 3  # average time between customer arrivals
SERVICE_TIME = 4      # average service duration
NUM_CASHIERS = 2      # number of cashiers

# Data Tracking
wait_times = []
queue_lengths = []


# Activity of the customer
def customer(env, name, cashier, service_time):
    arrival_time = env.now
    print(f"{name} arrives at {arrival_time:.2f}")

    with cashier.request() as request:
        yield request  # wait for available cashier
        wait = env.now - arrival_time #wait time as how much they waited till they get cashier
        wait_times.append(wait)
        print(f"{name} waited {wait:.2f} minutes")
        # Generate a random service time based on exponential distribution
        service_duration = random.expovariate(1.0 / service_time)
        yield env.timeout(service_duration)
        print(f"{name} finished service at {env.now:.2f}")


# Customer Generator
def customer_arrivals(env, cashier, arrival_interval, service_time):
    i = 0
    while True: # Keep generating customers until the simulation ends
        yield env.timeout(random.expovariate(1.0 / arrival_interval))
        i += 1
        env.process(customer(env, f"Customer {i}", cashier, service_time))
        queue_lengths.append(len(cashier.queue))


# Run Simulation Function
def run_simulation(num_cashiers, arrival_interval, service_time):
    global wait_times, queue_lengths
    wait_times, queue_lengths = [], []

    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    cashier = simpy.Resource(env, num_cashiers)
    env.process(customer_arrivals(env, cashier, arrival_interval, service_time))
    env.run(until=SIM_TIME)

    avg_wait = statistics.mean(wait_times) if wait_times else 0
    avg_queue = statistics.mean(queue_lengths) if queue_lengths else 0
    print("\n--- Simulation Summary ---")
    print(f"Cashiers: {num_cashiers}")
    print(f"Average Wait Time: {avg_wait:.2f} minutes")
    print(f"Average Queue Length: {avg_queue:.2f}")
    print(f"Customers Served: {len(wait_times)}\n")
    return avg_wait, avg_queue, len(wait_times)


# Run 4 Scenarios for testing 
if __name__ == "__main__":
    print("Fast Food Restaurant Queue Simulation\n")

    # Scenario 1 - base case
    run_simulation(num_cashiers=1, arrival_interval=3, service_time=4)

    # Scenario 2 - more cashiers
    run_simulation(num_cashiers=2, arrival_interval=3, service_time=4)

    # Scenario 3 - peak time
    run_simulation(num_cashiers=1, arrival_interval=2, service_time=4)

    # Scenario 4 - peak time with two cashier
    run_simulation(num_cashiers=2, arrival_interval=2, service_time=4)
