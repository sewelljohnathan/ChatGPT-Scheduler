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
def run_fifo():
    global time, previous_running_process

    eligible_processes = [process for process in processes if process.arrival_time <= time and process.status == "Ready"]
    if eligible_processes:

        # Get first in process
        running_process = eligible_processes[0]

        if running_process.response_time is None:
            running_process.response_time = time - running_process.arrival_time

        if running_process != previous_running_process:
            output.append(f"Time {time:4} : {running_process.name} selected (burst {running_process.burst_time:4})")
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
            output.append(f"Time {time:4} : {running_process.name} selected (burst {running_process.burst_time:4})")
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

rr_processes = []
rr_queueIndex = 0
def run_rr():
    global time, rr_processes, rr_queueIndex
    running_process = None

    # Check if there are any processes that have arrived but not started yet
    rr_processes += [process for process in processes if process not in rr_processes and process.arrival_time <= time]
    eligible_processes = [process for process in rr_processes if process.status == "Ready"]
    if eligible_processes:
        # Select the next process to run based on RR scheduling
        rr_queueIndex %= len(eligible_processes)
        running_process = eligible_processes[rr_queueIndex]
        rr_queueIndex += 1

        if running_process.response_time is None:
            running_process.response_time = time - running_process.arrival_time

        if running_process.remaining_time > quantum:
            output.append(f"Time {time:4} : {running_process.name} selected (burst {quantum:4})")
            running_process.remaining_time -= quantum
        else:
            output.append(f"Time {time:4} : {running_process.name} selected (burst {running_process.remaining_time:4})")
            output.append(f"Time {time + running_process.remaining_time:4} : {running_process.name} finished")
            running_process.remaining_time = 0
            running_process.status = "Finished"
            running_process.turnaround_time = time + quantum - running_process.arrival_time
            running_process.waiting_time = running_process.turnaround_time - running_process.burst_time
            
    else:
        output.append(f"Time {time:4} : Idle")

    time += quantum

# Print the number of processes and the selected algorithm
output.append(f"{process_count} processes")
output.append(f"Using {algorithm}")
if algorithm == "rr":
    output.append(f"Quantum {quantum}")

# Main scheduling loop
while time < run_for:
    if algorithm == "fifo":
        run_fifo()
    elif algorithm == "sjf":
        run_sjf()
    elif algorithm == "rr":
        run_rr()
    else:
        print(f"Error: Unknown scheduling algorithm '{algorithm}'")
        sys.exit(1)

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
