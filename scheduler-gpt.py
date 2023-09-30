#!/home/sewell/.pyenv/shims/python

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
output = []

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

# Initialize a global variable to keep track of the previous running process
previous_running_process = None

# Define scheduler functions
def run_fcfs():
    global time, previous_running_process

    eligible_processes = [process for process in processes if process.arrival_time <= time and process.status == "Ready"]

    # Print a message for each arriving process
    for process in eligible_processes:
        if process.arrival_time == time:
            output.append(f"Time {time:4} : {process.name} arrived") 

    if eligible_processes:

        # Get first in process
        running_process = eligible_processes[0]

        if running_process.response_time is None:
            running_process.response_time = time - running_process.arrival_time

        if running_process != previous_running_process:
            output.append(f"Time {time:4} : {running_process.name} selected (burst {running_process.remaining_time:4})")
            previous_running_process = running_process

        running_process.remaining_time -= 1

        # Finish
        if running_process.remaining_time == 0:
            running_process.status = "Finished"
            running_process.turnaround_time = time + 1 - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            output.append(f"Time {time + 1:4} : {running_process.name} finished")

    else:
        output.append(f"Time {time:4} : Idle")
    
    time += 1


def run_sjf():
    global time
    global previous_running_process  # Access the global variable

    running_process = None

    # Check if there are any processes that have arrived but not started yet
    eligible_processes = [process for process in processes if process.arrival_time <= time and process.status == "Ready"]

    # Print a message for each arriving process
    for process in eligible_processes:
        if process.arrival_time == time:
            output.append(f"Time {time:4} : {process.name} arrived") 

    if eligible_processes:
        # Find the process with the shortest remaining burst time
        running_process = min(eligible_processes, key=lambda x: x.remaining_time)
        if running_process.response_time is None:
            running_process.response_time = time - process.arrival_time

        # If the running process has changed, print a selection message
        if running_process != previous_running_process:
            output.append(f"Time {time:4} : {running_process.name} selected (burst {running_process.remaining_time:4})")
            previous_running_process = running_process

        running_process.remaining_time -= 1

        # Check if the process has finished executing
        if running_process.remaining_time == 0:
            running_process.status = "Finished"
            running_process.turnaround_time = time + 1 - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            output.append(f"Time {time+1:4} : {running_process.name} finished")
    else:
        output.append(f"Time {time:4} : Idle")

    time += 1

rr_processes = [process for process in processes if process.arrival_time == 0]
quantum_timer = 0
def run_rr():
    global time, rr_processes, previous_running_process, quantum_timer
    running_process = None

    for process in [p for p in processes if p.arrival_time <= time and p.response_time is None]:
        output.append(f"Time {process.arrival_time:4} : {process.name} arrived") 

    # Check if there are any processes that have arrived but not started yet
    if len(rr_processes) > 0:

        if previous_running_process is None or previous_running_process.status == "Finished" or quantum_timer % quantum == 0:
            running_process = rr_processes[0]
        else:
            running_process = previous_running_process

        if running_process != previous_running_process or quantum_timer % quantum == 0:
            output.append(f"Time {time:4} : {running_process.name} selected (burst {running_process.remaining_time:4})")

        if running_process.response_time is None:
            running_process.response_time = time - running_process.arrival_time

        previous_running_process = running_process

        quantum_timer += 1
        running_process.remaining_time -= 1

        if running_process.remaining_time == 0:
            output.append(f"Time {time + 1:4} : {running_process.name} finished")
            running_process.status = "Finished"
            running_process.turnaround_time = time + 1 - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            quantum_timer = 0

        rr_processes += [process for process in processes if process not in rr_processes and process.arrival_time <= time + 1 and process.status == "Ready"]
        rr_processes.remove(running_process)
        if running_process.status == "Ready":
            rr_processes.append(running_process)
            
    else:
        output.append(f"Time {time:4} : Idle")

    time += 1

# Print the number of processes and the selected algorithm
output.append(f"{process_count} processes")
output.append(f"Using {algorithm}")
if algorithm == "rr":
    output.append(f"Quantum {quantum}")

# Main scheduling loop
while time < run_for:
    if algorithm == "fcfs":
        run_fcfs()
    elif algorithm == "sjf":
        run_sjf()
    elif algorithm == "rr":
        run_rr()
    else:
        print(f"Error: Unknown scheduling algorithm '{algorithm}'")
        sys.exit(1)

# Calculate and print results
def calculate_metrics():

    output.append(f"Finished at time {time}")
    output.append("")

    for process in processes:
        if process.status != "Finished":
            output.append(f"{process.name} did not finish")

    output.append("")

    for process in processes:
        if process.status == "Finished":
            output.append(f"{process.name} wait {process.waiting_time:4} turnaround {process.turnaround_time:4} response {process.response_time:4}")

calculate_metrics()

# Write output to a file
output_file = input_file.replace(".in", ".out")
with open(output_file, 'w') as file:
    file.write('\n'.join(output))
