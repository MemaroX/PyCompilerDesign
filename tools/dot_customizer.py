import argparse
import graphviz
import sys
import re

def customize_dot_file(input_dot_path, output_dot_path, output_png_path=None):
    try:
        with open(input_dot_path, 'r') as f:
            dot_source = f.read()

        # Initialize a new Digraph
        graph = graphviz.Digraph(comment='Customized Graph')
        
        # Regex to find graph attributes (like rankdir)
        graph_attr_match = re.search(r'digraph\s*{\s*([^}]+)}', dot_source, re.DOTALL)
        if graph_attr_match:
            attrs_str = graph_attr_match.group(1)
            # Simple parsing for rankdir, can be extended for others
            rankdir_match = re.search(r'rankdir\s*=\s*([a-zA-Z]+)', attrs_str)
            if rankdir_match:
                graph.attr(rankdir=rankdir_match.group(1))

        # Regex to find node definitions and attributes
        # This is a simplified regex and might not catch all cases
        node_pattern = re.compile(r'node\s*\[([^\]]+)\];\s*([a-zA-Z0-9_]+(?:;\s*[a-zA-Z0-9_]+)*)')
        for match in node_pattern.finditer(dot_source):
            attrs_str = match.group(1)
            node_names_str = match.group(2)
            node_names = [n.strip() for n in node_names_str.split(';') if n.strip()]
            
            node_attrs = {}
            # Simple parsing for shape, can be extended
            shape_match = re.search(r'shape\s*=\s*([a-zA-Z]+)', attrs_str)
            if shape_match:
                node_attrs['shape'] = shape_match.group(1)
            
            for node_name in node_names:
                graph.node(node_name, **node_attrs)

        # Regex to find initial state (null -> State) and other nodes
        initial_state = None
        initial_match = re.search(r'null\s*->\s*([a-zA-Z0-9_]+)', dot_source)
        if initial_match:
            initial_state = initial_match.group(1)
            graph.node('', shape='none', width='0', height='0') # Re-add invisible null node
            graph.edge('', initial_state) # Re-add initial state edge

        # Regex to find edges (transitions)
        # This is a simplified regex and might not catch all cases
        edge_pattern = re.compile(r'([a-zA-Z0-9_]+)\s*->\s*([a-zA-Z0-9_]+)\s*\[label\s*=\s*"([^"]+)"\]')
        for match in edge_pattern.finditer(dot_source):
            from_node = match.group(1)
            to_node = match.group(2)
            label = match.group(3)
            graph.edge(from_node, to_node, label=label)

        # --- Customization Logic ---
        if initial_state:
            graph.node(initial_state, color='red', style='filled')
            print(f"Customized initial state '{initial_state}' to be red.")
        else:
            print("Could not identify initial state for customization.")

        # Save the modified DOT file
        graph.render(output_dot_path, view=False, format='dot', cleanup=True)
        print(f"Customized DOT saved to {output_dot_path}.dot")

        # Render to PNG if requested
        if output_png_path:
            graph.render(output_png_path, view=False, format='png', cleanup=True)
            print(f"Customized PNG saved to {output_png_path}.png")

    except FileNotFoundError:
        print(f"Error: Input DOT file not found at {input_dot_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during DOT customization: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Customize a DOT graph file.")
    parser.add_argument('--input', required=True, help="Path to the input DOT file.")
    parser.add_argument('--output', required=True, help="Base name for the output DOT and PNG files (e.g., 'custom_dfa').")
    parser.add_argument('--no-png', action='store_true', help="Do not generate a PNG image.")

    args = parser.parse_args()

    output_dot_base = args.output
    output_png_base = args.output if not args.no_png else None

    customize_dot_file(args.input, output_dot_base, output_png_base)