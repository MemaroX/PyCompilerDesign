import argparse
import sys
import os
import json
import subprocess
import graphviz

def get_input(prompt, validation_func=None, error_message="Invalid input. Please try again."):
    while True:
        user_input = input(prompt).strip()
        if validation_func:
            if validation_func(user_input):
                return user_input
            else:
                print(error_message)
        else:
            return user_input

def validate_list_input(input_str):
    return bool(input_str)

def validate_state_in_states(state, states):
    return state in states

def validate_symbol_in_alphabet(symbol, alphabet):
    return symbol in alphabet

def create_dot_file(automaton_data, filename="automaton_visualization"):
    automaton_type = automaton_data["type"]
    dot = graphviz.Digraph(comment=f'{automaton_type.upper()} Visualization')
    dot.attr('node', shape='circle')
    dot.attr(rankdir='LR')

    # Add invisible start node and edge to initial state
    dot.node('start', shape='none', width='0', height='0')
    dot.edge('start', automaton_data["initial"])

    # Add nodes
    for state in automaton_data["states"]:
        if state in automaton_data["final"]:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)

    # Add transitions
    if automaton_type == 'dfa':
        for (state, symbol), next_state in automaton_data["transitions"].items():
            dot.edge(state, next_state, label=str(symbol))
    elif automaton_type == 'nfa':
        for (state, symbol), next_states in automaton_data["transitions"].items():
            for next_state in next_states:
                dot.edge(state, next_state, label=str(symbol))

    output_path = f"{filename}.png"
    try:
        dot.render(filename, view=False, format='png', cleanup=True)
        print(f"Visualization saved to {output_path}")
    except graphviz.backend.gv.ExecutableNotFound:
        print(f"Warning: Graphviz executable 'dot' not found. Cannot generate visualization. Please ensure Graphviz is installed and in your system's PATH.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred during visualization: {e}", file=sys.stderr)

def main():
    print("--- Finite State Automaton Creator ---")

    automaton_type = get_input("Enter automaton type (dfa/nfa): ", lambda x: x in ['dfa', 'nfa'], "Type must be 'dfa' or 'nfa'.")

    alphabet_str = get_input("Enter alphabet symbols (comma-separated, e.g., '0,1'): ", validate_list_input)
    alphabet = tuple(s.strip() for s in alphabet_str.split(','))

    states_str = get_input("Enter state names (comma-separated, e.g., 'q0,q1,q2'): ", validate_list_input)
    states = tuple(s.strip() for s in states_str.split(','))

    initial_state = get_input(f"Enter initial state (must be one of {states}): ", lambda x: validate_state_in_states(x, states), f"Initial state must be in {states}.")

    final_states_str = get_input(f"Enter final state(s) (comma-separated, must be in {states}): ", validate_list_input)
    final_states = tuple(s.strip() for s in final_states_str.split(','))
    for fs in final_states:
        if not validate_state_in_states(fs, states):
            print(f"Error: Final state '{fs}' is not in the list of defined states: {states}")
            sys.exit(1)

    transitions = {}
    print("\n--- Enter Transitions ---")
    print("Format: 'from_state,symbol,to_state' (DFA) or 'from_state,symbol,to_state1,to_state2,...' (NFA)")
    print("Type 'done' when finished.")

    while True:
        transition_input = get_input("Enter transition: ").strip()
        if transition_input.lower() == 'done':
            break

        parts = tuple(s.strip() for s in transition_input.split(','))

        if len(parts) < 3:
            print("Error: Invalid transition format. Please try again.")
            continue

        from_state, symbol = parts[0], parts[1]
        to_states_input = parts[2:]

        if not validate_state_in_states(from_state, states):
            print(f"Error: From state '{from_state}' is not in defined states {states}. Please try again.")
            continue
        if not validate_symbol_in_alphabet(symbol, alphabet):
            print(f"Error: Symbol '{symbol}' is not in defined alphabet {alphabet}. Please try again.")
            continue
        
        valid_to_states = True
        for ts in to_states_input:
            if not validate_state_in_states(ts, states):
                print(f"Error: To state '{ts}' is not in defined states {states}. Please try again.")
                valid_to_states = False
                break
        if not valid_to_states:
            continue

        if automaton_type == 'dfa':
            if len(to_states_input) > 1:
                print("Error: DFA transitions must have only one 'to' state. Please try again.")
                continue
            transitions[(from_state, symbol)] = to_states_input[0]
        else: # NFA
            if (from_state, symbol) in transitions:
                transitions[(from_state, symbol)] += to_states_input
            else:
                transitions[(from_state, symbol)] = to_states_input

    automaton_data = {
        "type": automaton_type,
        "alphabet": alphabet,
        "states": states,
        "initial": initial_state,
        "final": final_states,
        "transitions": transitions
    }

    # Generate DOT file
    dot_filename = get_input("Enter base filename for DOT/PNG visualization (e.g., 'my_fsm', leave blank for 'automaton_visualization'): ")
    if not dot_filename:
        dot_filename = "automaton_visualization"
    create_dot_file(automaton_data, dot_filename)

    # Generate JSON file
    json_filename = get_input("Enter filename to save FSM as JSON (e.g., 'my_fsm.json', leave blank to skip): ")
    if json_filename:
        try:
            # Convert tuple keys in transitions to string keys for JSON serialization
            json_transitions = {f"{k[0]},{k[1]}": v for k, v in transitions.items()}
            json_data = automaton_data.copy()
            json_data["transitions"] = json_transitions

            with open(json_filename, 'w') as f:
                json.dump(json_data, f, indent=4)
            print(f"FSM saved to {json_filename}")
        except Exception as e:
            print(f"Error saving JSON file: {e}", file=sys.stderr)

    # Offer to launch main3-0.py
    launch_main = get_input("Launch main3-0.py to test this FSM? (yes/no): ", lambda x: x.lower() in ['yes', 'no'], "Please enter 'yes' or 'no'.").lower()
    if launch_main == 'yes':
        if json_filename and os.path.exists(json_filename):
            print(f"Launching main3-0.py with {json_filename}...")
            try:
                # Adjusted path for main3-0.py within PyCompilerDesign
                subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "main3-0.py"), "--load-from", json_filename])
            except FileNotFoundError:
                print("Error: main3-0.py not found. Make sure it's in the same directory.", file=sys.stderr)
            except Exception as e:
                print(f"An error occurred while launching main3-0.py: {e}", file=sys.stderr)
        else:
            print("Cannot launch main3-0.py: JSON file not saved or not found.", file=sys.stderr)

    print("\n--- FSM Creation Complete ---")

if __name__ == "__main__":
    main()
