import sys

# Define a data structure for processes
class Process:
    def __init__(self, name, arrival_time, burst_time):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.status = "Ready"
        self.remaining_time = burst_time
        self.response_time = None
        self.waiting_time = None
        self.turnaround_time = None

# Initialize variables
processes = []
algorithm = ""
quantum = 0
time = 0

# Read input from the file
if len(sys.argv) != 2:
    print("Usage: scheduler-gpt.py <input file>")
    sys.exit(1)

input_file = sys.argv[1]
with open(input_file, 'r') as file:
    lines = file.readlines()

# Parse input
end_of_directives = False  # Flag to track the end of directives
for line in lines:
    tokens = line.strip().split()
    directive = tokens[0]
    
    if directive == "processcount":
        process_count = int(tokens[1])
    elif directive == "runfor":
        run_for = int(tokens[1])
    elif directive == "use":
        algorithm = tokens[1]
    elif directive == "quantum":  # Check for quantum directive
        quantum = int(tokens[1])  # Extract the quantum value
    elif directive == "process":
        name = tokens[2]
        arrival_time = int(tokens[4])
        burst_time = int(tokens[6])
        processes.append(Process(name, arrival_time, burst_time))
    elif directive == "end":  # Check for the end directive
        end_of_directives = True
        break  # Exit the loop if "end" is encountered

# Check if the end of directives is reached
if not end_of_directives:
    print("Error: Missing 'end' directive.")
    sys.exit(1)

# Sort processes by arrival time
processes.sort(key=lambda x: x.arrival_time)

# Define scheduler functions
def run_fifo():
    global time
    running_process = None

    # Check if there are any processes that have arrived but not started yet
    for process in processes:
        if process.arrival_time <= time and process.status == "Ready":
            running_process = process
            break

    if running_process is not None:
        running_process.status = "Running"
        print(f"Time {time:4} : {running_process.name} selected (burst {running_process.burst_time:4})")
        running_process.remaining_time -= 1

        # Check if the process has finished executing
        if running_process.remaining_time == 0:
            running_process.status = "Finished"
            running_process.turnaround_time = time + 1 - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            print(f"Time {time:4} : {running_process.name} finished")
    else:
        print(f"Time {time:4} : Idle")


# Initialize a global variable to keep track of the previous running process
previous_running_process = None

def run_sjf():
    global time
    global previous_running_process  # Access the global variable

    running_process = None

    # Check if there are any processes that have arrived but not started yet
    eligible_processes = [process for process in processes if process.arrival_time <= time and process.status == "Ready"]

    # Print a message for each arriving process
    for process in eligible_processes:
        if process.arrival_time == time:
            print(f"Time {time:4} : {process.name} arrived") 

    if eligible_processes:
        # Find the process with the shortest remaining burst time
        running_process = min(eligible_processes, key=lambda x: x.remaining_time)
        if running_process.response_time is None:
            running_process.response_time = time - process.arrival_time

        # If the running process has changed, print a selection message
        if running_process != previous_running_process:
            print(f"Time {time:4} : {running_process.name} selected (burst {running_process.burst_time:4})")
            previous_running_process = running_process

        running_process.remaining_time -= 1

        # Check if the process has finished executing
        if running_process.remaining_time == 0:
            running_process.status = "Finished"
            running_process.turnaround_time = time + 1 - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            print(f"Time {time+1:4} : {running_process.name} finished")
    else:
        print(f"Time {time:4} : Idle")


def run_rr():
    global time
    running_process = None

    # Check if there are any processes that have arrived but not started yet
    eligible_processes = [process for process in processes if process.arrival_time <= time and process.status == "Ready"]

    if eligible_processes:
        # Select the next process to run based on RR scheduling
        running_process = eligible_processes[0]

        if running_process.remaining_time > quantum:
            print(f"Time {time:4} : {running_process.name} selected (burst {quantum:4})")
            running_process.remaining_time -= quantum
        else:
            print(f"Time {time:4} : {running_process.name} selected (burst {running_process.remaining_time:4})")
            running_process.remaining_time = 0
            running_process.status = "Finished"
            running_process.turnaround_time = time + 1 - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            print(f"Time {time:4} : {running_process.name} finished")
    else:
        print(f"Time {time:4} : Idle")

    # Rotate the processes in the queue
    if running_process is not None and running_process.remaining_time > 0:
        eligible_processes.remove(running_process)
        eligible_processes.append(running_process)

# Print the number of processes and the selected algorithm
print(f"{process_count} processes")
print(f"Using {algorithm}")

# Main scheduling loop
while time < run_for:
    if algorithm == "fcfs":
        run_fifo()
    elif algorithm == "sjf":
        run_sjf()
    elif algorithm == "rr":
        run_rr()
    else:
        print(f"Error: Unknown scheduling algorithm '{algorithm}'")
        sys.exit(1)

    time += 1

# Calculate and print results
def calculate_metrics():
    total_turnaround_time = 0
    total_waiting_time = 0
    total_response_time = 0

    for process in processes:
        if process.status == "Finished":
            total_turnaround_time += process.turnaround_time
            total_waiting_time += process.waiting_time
            total_response_time += process.response_time

    print(f"Finished at time {time}")
    print()

    for process in processes:
        if process.status != "Finished":
            print(f"{process.name} did not finish")

    print()

    for process in processes:
        if process.status == "Finished":
            print(f"{process.name} wait {process.waiting_time:4} turnaround {process.turnaround_time:4} response {process.response_time:4}")

calculate_metrics()

# Write output to a file
output_file = input_file.replace(".in", ".out")
with open(output_file, 'w') as file:
    pass  # Implement output writing here
