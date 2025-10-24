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
service_times = [] #actual service duration


# Activity of the customer
def customer(env, name, cashier, avg_service_time):
    arrival_time = env.now
    print(f"{name} arrives at {arrival_time:.2f}")

    with cashier.request() as request:
        yield request  # wait for available cashier
        wait = env.now - arrival_time #wait time as how much they waited till they get cashier
        wait_times.append(wait)
        print(f"{name} waited {wait:.2f} minutes")
       
        # Generate a random service time based on exponential distribution
        service_duration = random.expovariate(1.0 / avg_service_time)
        service_times.append(service_duration)  #tracking service times
        yield env.timeout(service_duration)
        print(f"{name} finished service at {env.now:.2f}")


# Customer Generator
def customer_arrivals(env, cashier, arrival_interval, avg_service_time):
    i = 0
    while True: # Keep generating customers until the simulation ends
        yield env.timeout(random.expovariate(1.0 / arrival_interval))
        i += 1
        env.process(customer(env, f"Customer {i}", cashier, avg_service_time))
        queue_lengths.append(len(cashier.queue))


# Run Simulation Function
def run_simulation(num_cashiers, arrival_interval, avg_service_time, scenario_name):
    global wait_times, queue_lengths, service_times
    wait_times, queue_lengths, service_times = [], [], []

    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    cashier = simpy.Resource(env, num_cashiers)
    env.process(customer_arrivals(env, cashier, arrival_interval, avg_service_time))
    env.run(until=SIM_TIME)

    #calculate metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    avg_queue = statistics.mean(queue_lengths) if queue_lengths else 0
    throughput = len(wait_times) / SIM_TIME  # customers per minute
    #calculate utilization 
    total_service_time = sum(service_times) if service_times else 0
    total_possible_time = num_cashiers * SIM_TIME
    utilization = (total_service_time / total_possible_time) * 100 if total_possible_time > 0 else 0
   
    print(f"\n--- {scenario_name} Simulation Summary ---")
    print(f"Cashiers: {num_cashiers}")
    print(f"Average Wait Time: {avg_wait:.2f} minutes") #response time
    print(f"Average Queue Length: {avg_queue:.2f}") #systemload
    print(f"Throughput: {throughput:.2f} customers/minute")
    print(f"Utilization: {utilization:.2f}%") #utilization
    print(f"Customers Served: {len(wait_times)}\n") #throuput
    return{
        'scenario': scenario_name,
        'avg_wait': avg_wait,
        'avg_queue':avg_queue,
        'throughput': throughput,
        'utilization': utilization,
        'customers_served': len(wait_times),
        'wait_times': wait_times.copy(),
        'service_times': service_times.copy()
    }
# Run 4 Scenarios for testing 
if __name__ == "__main__":
    print("Fast Food Restaurant Queue Simulation\n")

    #collect result for table
    results = []
    # Scenario 1 - base case
    results.append(run_simulation(num_cashiers=1, arrival_interval=3, avg_service_time=4, scenario_name= "Base Case"))

    # Scenario 2 - more cashiers
    results.append(run_simulation(num_cashiers=2, arrival_interval=3, avg_service_time=4, scenario_name= "More Cashier"))

    # Scenario 3 - peak time
    results.append(run_simulation(num_cashiers=1, arrival_interval=2, avg_service_time=4, scenario_name= "Peak Time"))

    # Scenario 4 - peak time with two cashier
    results.append(run_simulation(num_cashiers=2, arrival_interval=2, avg_service_time=4, scenario_name= "Peak + More Cashiers"))


    # Create Summary Table
    print("\n" + "="*80)
    print("--- EXPERIMENT SUMMARY TABLE ---")
    print("="*80)
    
    # Header
    print(f"{'Scenario':<20} {'Avg Wait':<12} {'Avg Queue':<12} {'Throughput':<12} {'Utilization(%)':<15} {'Served':<8}")
    print("-" * 80)
    
    # Data rows
    for result in results:
        print(f"{result['scenario']:<20} {result['avg_wait']:<12.2f} {result['avg_queue']:<12.2f} {result['throughput']:<12.3f} {result['utilization']:<15.2f} {result['customers_served']:<8}")


    print("\n--- Simulation Complete! ---")
    
    print("--- Good Bye! ---")