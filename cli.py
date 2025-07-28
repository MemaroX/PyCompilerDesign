import argparse
import sys
import os
import json
# from python_fsa import DFA, NFA # Original import
from compiler.fsa import DFA, NFA # Adjusted import
import graphviz

def serialize_automaton(automaton):
    # Convert automaton object to a dictionary for JSON serialization
    data = {
        "type": "dfa" if isinstance(automaton, DFA) else "nfa",
        "alphabet": list(automaton.alphabet),
        "states": list(automaton.states),
        "initial": automaton.initial,
        "final": list(automaton.final),
        "transitions": {}
    }
    for (state, symbol), next_state_or_states in automaton.transitions.items():
        key = f"{state},{symbol}"
        if isinstance(automaton, DFA):
            data["transitions"][key] = next_state_or_states
        else: # NFA
            data["transitions"][key] = list(next_state_or_states)
    return data

def deserialize_automaton(data):
    # Reconstruct automaton object from a dictionary
    automaton_type = data["type"]
    alphabet = tuple(data["alphabet"])
    states = tuple(data["states"])
    initial = data["initial"]
    final = tuple(data["final"])
    transitions = {}

    for key, value in data["transitions"].items():
        state, symbol = key.split(',')
        if automaton_type == "dfa":
            transitions[(state, symbol)] = value
        else: # NFA
            transitions[(state, symbol)] = tuple(value)

    if automaton_type == "dfa":
        return DFA(alphabet=alphabet, states=states, initial=initial, final=final, transitions=transitions)
    else:
        return NFA(alphabet=alphabet, states=states, initial=initial, final=final, transitions=transitions)

def visualize_automaton(automaton, automaton_type, filename="automaton_visualization"):
    dot = graphviz.Digraph(comment=f'{automaton_type.upper()} Visualization')
    dot.attr('node', shape='circle')
    dot.attr(rankdir='LR')

    # Add invisible start node and edge to initial state
    dot.node('start', shape='none', width='0', height='0')
    dot.edge('start', automaton.initial)

    # Add nodes
    for state in automaton.states:
        if state in automaton.final:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)

    # Add transitions
    if automaton_type == 'dfa':
        for (state, symbol), next_state in automaton.transitions.items():
            dot.edge(state, next_state, label=str(symbol))
    elif automaton_type == 'nfa':
        for (state, symbol), next_states in automaton.transitions.items():
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

def parse_dot_file(dot_filepath):
    try:
        with open(dot_filepath, 'r') as f:
            dot_source = f.read()
        
        # Use graphviz.Source to parse the dot file
        graph = graphviz.Source(dot_source)
        
        # This is a simplified parsing. A robust parser would need to handle
        # all DOT syntax variations, subgraphs, attributes, etc.
        # For this example, we'll assume a basic structure as seen in dfa_example.gv and nfa_example.gv

        states = set()
        alphabet = set()
        transitions = {}
        initial_state = None
        final_states = set()
        automaton_type = 'dfa' # Assume DFA unless NFA characteristics are found

        # Parse nodes and initial/final states
        # This part is tricky as graphviz.Source doesn't directly expose parsed AST
        # We'll rely on string parsing for simplicity, but it's brittle.
        lines = dot_source.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('node [shape = doublecircle]'):
                parts = line.split(';')
                for part in parts:
                    if 'doublecircle' in part:
                        state_name = part.replace('node [shape = doublecircle]', '').strip()
                        if state_name:
                            final_states.add(state_name)
                            states.add(state_name)
            elif line.startswith('node [shape = circle]'):
                # Regular states, already added if they are final or in transitions
                pass
            elif '->' in line and not line.startswith('null ->'):
                # Parse transitions
                parts = line.split('->')
                from_state = parts[0].strip()
                to_part = parts[1].strip()

                label_match = to_part.split('label = "')
                if len(label_match) > 1:
                    label_str = label_match[1].split('"')[0]
                    to_state = label_match[0].strip().replace(' [', '').strip()
                else:
                    to_state = to_part.strip()
                    label_str = "" # Epsilon transition or unlabeled
                
                symbols = tuple(s.strip() for s in label_str.split(',')) if label_str else ("",)

                states.add(from_state)
                states.add(to_state)
                for symbol in symbols:
                    if symbol:
                        alphabet.add(symbol)

                for symbol in symbols:
                    current_transitions = transitions.get((from_state, symbol), [])
                    current_transitions.append(to_state)
                    transitions[(from_state, symbol)] = current_transitions
                    
                    # Check for NFA characteristics
                    if len(current_transitions) > 1:
                        automaton_type = 'nfa'

            elif line.startswith('null ->'):
                initial_state = line.replace('null ->', '').strip().replace(';', '').strip()
                states.add(initial_state)

        # Convert transition lists to tuples/single values
        processed_transitions = {}
        for (state, symbol), next_states_list in transitions.items():
            if automaton_type == 'dfa':
                if len(next_states_list) != 1:
                    raise ValueError(f"DFA transition from {state} on {symbol} leads to multiple states: {next_states_list}. This is not a valid DFA.")
                processed_transitions[(state, symbol)] = next_states_list[0]
            else:
                processed_transitions[(state, symbol)] = tuple(sorted(set(next_states_list))) # Remove duplicates and sort for consistency

        # Ensure all states in transitions are in the states set
        for (s, _), next_s in processed_transitions.items():
            if s not in states:
                states.add(s)
            if isinstance(next_s, tuple):
                for ns in next_s:
                    if ns not in states:
                        states.add(ns)
            elif next_s not in states:
                states.add(next_s)

        if automaton_type == 'dfa':
            return DFA(
                alphabet=frozenset(alphabet),
                states=frozenset(states),
                initial=initial_state,
                final=frozenset(final_states),
                transitions=processed_transitions
            ), 'dfa'
        else:
            return NFA(
                alphabet=frozenset(alphabet),
                states=frozenset(states),
                initial=initial_state,
                final=frozenset(final_states),
                transitions=processed_transitions
            ), 'nfa'

    except FileNotFoundError:
        print(f"Error: DOT file not found at {dot_filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing DOT file {dot_filepath}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Create and test a Finite State Automaton.")
    parser.add_argument('--type', choices=['dfa', 'nfa'], help="Type of automaton to create (dfa or nfa). Required if not loading from file or DOT file.")
    parser.add_argument('--alphabet', help="Comma-separated list of alphabet symbols (e.g., '0,1'). Required if not loading from file or DOT file.")
    parser.add_argument('--states', help="Comma-separated list of state names (e.g., 'q0,q1,q2'). Required if not loading from file or DOT file.")
    parser.add_argument('--initial', help="Name of the initial state. Required if not loading from file or DOT file.")
    parser.add_argument('--final', help="Comma-separated list of final state names. Required if not loading from file or DOT file.")
    parser.add_argument('--transitions', nargs='+', help="List of transitions, each in the format 'state,symbol,next_state' (e.g., q0,0,q1 q0,1,q2). For NFAs, you can specify multiple next states like 'q0,1,q0,q1'. Required if not loading from file or DOT file.")
    parser.add_argument('--output-file', help="Optional: Filename for the visualization (e.g., 'my_automaton'). Default is 'automaton_visualization'.")
    parser.add_argument('--skip-visualization', action='store_true', help="Skip generating the visualization image.")
    parser.add_argument('--save-to', help="Optional: Save the created automaton to a JSON file.")
    parser.add_argument('--load-from', help="Optional: Load an automaton from a JSON file. If provided, other automaton definition arguments are ignored.")
    parser.add_argument('--dot-file', help="Optional: Load an automaton from a DOT graph description file. If provided, other automaton definition arguments are ignored.")

    args = parser.parse_args()

    automaton = None
    automaton_type = None

    if args.load_from:
        try:
            with open(args.load_from, 'r') as f:
                data = json.load(f)
            automaton = deserialize_automaton(data)
            automaton_type = data["type"]
            print(f"\nAutomaton loaded successfully from {args.load_from}!")
        except FileNotFoundError:
            print(f"Error: File not found at {args.load_from}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {args.load_from}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred while loading automaton: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.dot_file:
        automaton, automaton_type = parse_dot_file(args.dot_file)
        print(f"\nAutomaton loaded successfully from {args.dot_file}!")
    else:
        # Validate required arguments if not loading from file
        if not all([args.type, args.alphabet, args.states, args.initial, args.final, args.transitions]):
            parser.error("When not loading from a file or DOT file, --type, --alphabet, --states, --initial, --final, and --transitions are all required.")

        # --- Process Arguments ---
        automaton_type = args.type
        alphabet = tuple(s.strip() for s in args.alphabet.split(','))
        states = tuple(s.strip() for s in args.states.split(','))
        initial = args.initial.strip()
        final_states = tuple(s.strip() for s in args.final.split(','))

        if initial not in states:
            print(f"Error: Initial state '{initial}' is not in the list of defined states: {states}", file=sys.stderr)
            sys.exit(1)

        for state in final_states:
            if state not in states:
                print(f"Error: Final state '{state}' is not in the list of defined states: {states}", file=sys.stderr)
                sys.exit(1)

        # --- Build Transition Table ---
        transitions = {}
        if automaton_type == 'dfa':
            for t in args.transitions:
                parts = tuple(s.strip() for s in t.split(','))
                if len(parts) != 3:
                    print(f"Error: Invalid DFA transition format: '{t}'. Expected 'state,symbol,next_state'.", file=sys.stderr)
                    sys.exit(1)
                state, symbol, next_state = parts
                if state not in states:
                    print(f"Error: Transition '{t}': State '{state}' is not defined in states: {states}", file=sys.stderr)
                    sys.exit(1)
                if symbol not in alphabet:
                    print(f"Error: Transition '{t}': Symbol '{symbol}' is not defined in alphabet: {alphabet}", file=sys.stderr)
                    sys.exit(1)
                if next_state not in states:
                    print(f"Error: Transition '{t}': Next state '{next_state}' is not defined in states: {states}", file=sys.stderr)
                    sys.exit(1)
                if (state, symbol) in transitions:
                    print(f"Error: Duplicate DFA transition for ({state}, {symbol}). DFA transitions must be unique.", file=sys.stderr)
                    sys.exit(1)
                transitions[(state, symbol)] = next_state
        else: # NFA
            for t in args.transitions:
                parts = tuple(s.strip() for s in t.split(','))
                if len(parts) < 3:
                    print(f"Error: Invalid NFA transition format: '{t}'. Expected 'state,symbol,next_state1,next_state2,...'.", file=sys.stderr)
                    sys.exit(1)
                state, symbol = parts[0], parts[1]
                next_states_for_transition = tuple(parts[2:])

                if state not in states:
                    print(f"Error: Transition '{t}': State '{state}' is not defined in states: {states}", file=sys.stderr)
                    sys.exit(1)
                if symbol not in alphabet:
                    print(f"Error: Transition '{t}': Symbol '{symbol}' is not defined in alphabet: {alphabet}", file=sys.stderr)
                    sys.exit(1)
                for ns in next_states_for_transition:
                    if ns not in states:
                        print(f"Error: Transition '{t}': Next state '{ns}' is not defined in states: {states}", file=sys.stderr)
                        sys.exit(1)
                
                if (state, symbol) in transitions:
                    transitions[(state, symbol)] += next_states_for_transition
                else:
                    transitions[(state, symbol)] = next_states_for_transition

        # --- Create Automaton ---
        if automaton_type == 'dfa':
            automaton = DFA(
                alphabet=alphabet,
                states=states,
                initial=initial,
                final=final_states,
                transitions=transitions
            )
            print(f"\n{automaton_type.upper()} created successfully!")
        else:
            automaton = NFA(
                alphabet=alphabet,
                states=states,
                initial=initial,
                final=final_states,
                transitions=transitions
            )
            print(f"\n{automaton_type.upper()} created successfully!")

    # --- Save Automaton (if requested) ---
    if args.save_to:
        try:
            with open(args.save_to, 'w') as f:
                json.dump(serialize_automaton(automaton), f, indent=4)
            print(f"Automaton saved to {args.save_to}")
        except Exception as e:
            print(f"Error saving automaton to file: {e}", file=sys.stderr)

    # --- Visualization (if not skipped) ---
    if not args.skip_visualization:
        output_filename = args.output_file if args.output_file else f"{automaton_type}_visualization"
        visualize_automaton(automaton, automaton_type, output_filename)

    # --- Interactive Testing ---
    print("\n--- Interactive Testing ---")
    print(f"Enter strings over the alphabet {automaton.alphabet} (comma-separated for multi-character symbols, e.g., 'a,b,c').")
    print("Type 'exit' to quit.")
    print("Type 'step' to process input symbol by symbol.")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue
            
            input_symbols = tuple(user_input.split(',')) if ',' in user_input else tuple(user_input)

            # Validate input symbols against the automaton's alphabet
            invalid_symbols = [s for s in input_symbols if s not in automaton.alphabet]
            if invalid_symbols:
                print(f"Error: Input contains symbols not in the defined alphabet {automaton.alphabet}: {invalid_symbols}", file=sys.stderr)
                continue

            if user_input.lower() == 'step':
                print("\n--- Step-by-Step Execution ---")
                current_transducer = automaton.transducer()
                current_state = current_transducer.current
                print(f"Initial state: {current_state}")
                step_input = input(f"Enter symbol to process (or 'done'): ").strip()
                while step_input.lower() != 'done':
                    if step_input not in automaton.alphabet:
                        print(f"Error: Symbol '{step_input}' not in alphabet {automaton.alphabet}", file=sys.stderr)
                    else:
                        current_transducer.push(step_input)
                        current_state = current_transducer.current
                        print(f"Processed '{step_input}'. Current state: {current_state}. Accepting: {current_transducer.is_accepting}")
                    step_input = input(f"Enter symbol to process (or 'done'): ").strip()
                print("--- End Step-by-Step Execution ---")
            else:
                if automaton.accepts(input_symbols):
                    print("  -> Accepted")
                else:
                    print("  -> Rejected")
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            break
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
