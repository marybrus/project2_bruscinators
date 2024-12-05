from tabulate import tabulate
from typing import List, Tuple, Dict

# NTM class
class NonDeterministicTuringMachine:
  # Initial components of the NTM including transitions, start state, accept state, reject state, machine name, and max depth
  def __init__(self, file_path: str):
      self.transitions = {}
      self.start_state = None
      self.accept_state = None
      self.reject_state = None
      self.machine_name = None
      self.max_depth = None
      self.load_machine(file_path)

  def load_machine(self, file_path: str):
    # Takes the NTM file and parses it
    with open(file_path, 'r') as file:
        lines = file.read().strip().split('\n')

        # Parses the headers
        self.machine_name = lines[0].strip()
        self.start_state = lines[4].strip()
        self.accept_state = lines[5].strip()
        self.reject_state = lines[6].strip()

        # Parse transitions, adds them to a dictionary of lists
        for line in lines[7:]:
            current_state, read_symbol, next_state, write_symbol, direction = line.split(',')
            key = (current_state, read_symbol)
            if key not in self.transitions:
                self.transitions[key] = []
            self.transitions[key].append((next_state, write_symbol, direction))

  def run(self, input_string: str, max_depth: int):
    # Initialize the simulation
    self.max_depth = max_depth
    initial_tape = list(input_string) + ['_']
    initial_config = (self.start_state, 0, initial_tape)
    tree = [[initial_config]]

    transitions_simulated = 0
    total_configurations_per_level = []  

    # Adds to results to make the table 
    result = {
      "String": input_string,
      "Accepted": False,
      "Depth": 0,
      "Configurations": 0,
      "Nondeterminism": 0.0,
      "Comments": "Chosen as a sanity check to ensure the program works as anticipated."
    }

    # Open the output file and append the machine and initial string 
    with open("output_bruscinators.txt", "a") as file:
      file.write(f"\nMachine: {self.machine_name}\nInitial string: '{input_string}'\n")
      print(f"\nMachine: {self.machine_name}")
      print(f"Initial string: '{input_string}'")

    # Find the depth of the string
    for depth in range(max_depth):
      current_level = tree[-1]
      next_level = []

      # Record the number of configurations at this level
      total_configurations_per_level.append(len(current_level))

      for state, head, tape in current_level:
        self.print_configuration(state, head, tape)

        if state == self.accept_state:
            accepting_path = self.trace_path(tree, (state, head, tape))
            result["Accepted"] = True
            result["Depth"] = len(accepting_path) - 1
            result["Configurations"] = transitions_simulated
            result["Nondeterminism"] = sum(total_configurations_per_level) / len(total_configurations_per_level)
            
            # Print and append to file if the string is accepted
            with open("output_bruscinators.txt", "a") as file:
                file.write(f"String accepted in {len(accepting_path) - 1} transitions.\n")
                print(f"String accepted in {len(accepting_path) - 1} transitions.")
            self.print_path(accepting_path)
            return result

        read_symbol = tape[head] if head < len(tape) else '_'
        key = (state, read_symbol)

        # Read the transitions
        if key in self.transitions:
            for next_state, write_symbol, direction in self.transitions[key]:
                new_tape = tape[:]
                if head < len(new_tape):
                    new_tape[head] = write_symbol
                else:
                    new_tape.append(write_symbol)

                new_head = head + (1 if direction == 'R' else -1)
                if new_head < 0:
                    new_head = 0

                next_level.append((next_state, new_head, new_tape))
                transitions_simulated += 1

      if not next_level:
        result["Depth"] = depth + 1
        result["Configurations"] = transitions_simulated
        result["Nondeterminism"] = sum(total_configurations_per_level) / len(total_configurations_per_level) if total_configurations_per_level else 0

        # Print if string rejected
        with open("output_bruscinators.txt", "a") as file:
          file.write(f"String rejected in {depth + 1} transitions.\n")
          print(f"String rejected in {depth + 1} transitions.")
        return result

      tree.append(next_level)

    result["Configurations"] = transitions_simulated
    result["Nondeterminism"] = sum(total_configurations_per_level) / len(total_configurations_per_level) if total_configurations_per_level else 0
    print(f"Execution stopped after {max_depth} transitions.")
    with open("output_bruscinators.txt", "a") as file:
      file.write(f"Execution stopped after {max_depth} transitions.\n")
    return result


  # This function traces the entirety of the tree to find the path
  def trace_path(self, tree, final_config):
    path = [final_config]
    for level in reversed(tree[:-1]):
      for config in level:
        if self.is_parent(config, path[-1]):
          path.append(config)
          break
    return list(reversed(path))

  # This function checks if the configuration is the parent of another
  def is_parent(self, parent, child):
    state, head, tape = parent
    next_state, next_head, next_tape = child
    read_symbol = tape[head] if head < len(tape) else '_'
    key = (state, read_symbol)
    if key in self.transitions:
      for ns, ws, d in self.transitions[key]:
        if ns == next_state:
          if next_tape[head] == ws and next_head == head + (1 if d == 'R' else -1):
            return True
    return False

  # This function is used to print the configuration and write it to an output file
  def print_configuration(self, state, head, tape):
    left_of_head = ''.join(tape[:head])
    head_char = tape[head] if head < len(tape) else '_'
    right_of_head = ''.join(tape[head + 1:])
    with open("output_bruscinators.txt", "a") as file:
      file.write(f"{left_of_head} [{state}] {head_char} {right_of_head}\n")
    print(f"{left_of_head} [{state}] {head_char} {right_of_head}")

  # Prints and writes the unique trace path of configurations only once
  def print_path(self, path):
    with open("output_bruscinators.txt", "a") as file:
      file.write("\nTrace Path of Accepting Configurations:\n")
      print("\nTrace Path of Accepting Configurations:")
      for state, head, tape in path:
        left_of_head = ''.join(tape[:head])
        head_char = tape[head] if head < len(tape) else '_'
        right_of_head = ''.join(tape[head + 1:])
        line = f"{left_of_head} [{state}] {head_char} {right_of_head}"
        file.write(line + "\n")
        print(line)
      print()



# Load and simulate the NTM with example inputs
file_path = 'a_plus_bruscinators.csv'
ntm = NonDeterministicTuringMachine(file_path)

# Inputs to test
inputs = ["", "a", "aaa"]
results = []

for input_string in inputs:
  results.append(ntm.run(input_string, max_depth=15))

# Print results as a table
print("\nSummary Table (Machine: a plus):")
print(tabulate(results, headers="keys", tablefmt="grid"))
with open("table_bruscinators.txt", "w") as file:
  file.write("Summary Table (Machine: a plus):\n")
  file.write(tabulate(results, headers="keys", tablefmt="grid"))
