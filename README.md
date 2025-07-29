# PyCompilerDesign: A Comprehensive Toolkit for Automata and Language Processing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Unlocking the World of Compilers and Formal Languages

`PyCompilerDesign` is an evolving Python project designed to provide a robust and intuitive toolkit for exploring, designing, and analyzing fundamental concepts in compiler design and formal language theory. Building upon the foundational principles of Finite State Automata (FSA), this project extends capabilities to include regular expression processing, interactive FSM creation, and advanced command-line utilities. Unlike traditional compiler front-ends, this project delves deep into the theoretical underpinnings of language recognition.

## Project Structure

```
PyCompilerDesign/
├── compiler/
│   └── fsa/
│       ├── __init__.py
│       ├── dfa.py
│       ├── nfa.py
│       └── regex.py
├── tools/
│   ├── cli.py
│   ├── dot_customizer.py
│   ├── fsm_creator.py
│   └── visualization.py # (Implicitly used for Graphviz integration)
├── main.py
├── pyproject.toml
├── README.md
└── LICENSE
```

-   **`compiler/fsa/`**: Contains the core Finite State Automata (FSA) implementation, including Deterministic Finite Automata (DFA), Nondeterministic Finite Automata (NFA), and Regular Expression (Regex) to NFA conversion logic.
-   **`tools/`**: Houses various command-line utilities for interacting with the FSA module, such as FSM creation, advanced CLI for testing, and DOT file customization.
-   **`main.py`**: The main entry point for interactive demonstrations of regex to NFA conversion and string acceptance.
-   **`pyproject.toml`**: Project metadata and dependency management.
-   **`README.md`**: This file, providing an overview of the project.
-   **`LICENSE`**: The project's license.

## Key Features

-   **DFA & NFA Implementation:** Core classes for Deterministic Finite Automata (DFAs) and Nondeterministic Finite Automata (NFAs), enabling the simulation and analysis of computational processes.
-   **Input Acceptance Testing:** Determine whether input strings are accepted or rejected by defined automata.
-   **NFA to DFA Conversion:** Seamlessly convert NFAs to their equivalent DFAs, simplifying analysis and understanding.
-   **Transducers:** Explore step-by-step computation with mutable transducers that process input symbols one at a time.
-   **Regular Expression Integration:** Define automata directly from regular expression patterns, bridging the gap between theoretical language definition and practical automaton construction.
-   **Interactive FSM Creation (`tools/fsm_creator.py`):** An intuitive command-line interface to guide you through the process of defining DFAs and NFAs, generating both JSON definitions and visual DOT graph files.
-   **Advanced CLI (`tools/cli.py`):** A versatile command-line interface for loading, testing, and interacting with FSMs from various sources (JSON, DOT files), including a mesmerizing step-by-step execution mode.
-   **DOT File Customization (`tools/dot_customizer.py`):** Programmatically modify and render DOT graph files, allowing for enhanced visualization and emphasis of specific automaton elements.
-   **Visualization:** Integration with Graphviz to transform abstract mathematical concepts into visual diagrams (PNG), providing clear insights into automaton structure and behavior.

## Installation

`PyCompilerDesign` leverages `pygraphviz` for its visualization capabilities, which requires the Graphviz C library. Follow these steps to set up your environment:

1.  **Install Graphviz:** Download and install Graphviz from the [official website](https://graphviz.org/download/). Ensure that the `dot` executable is added to your system's PATH environment variable during installation.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/MemaroX/PyCompilerDesign.git
    cd PyCompilerDesign
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install .
    ```
    This command will install `pygraphviz` and other necessary dependencies defined in `pyproject.toml`.

## Usage

### Main Application (`main.py`)

Run the main application to interactively test regular expression to NFA conversion and string acceptance.

```bash
python main.py
```

Follow the prompts to enter a regular expression and test strings against the generated NFA.

### Interactive FSM Creation (`tools/fsm_creator.py`)

Create new DFAs or NFAs through a guided interactive process.

```bash
python tools/fsm_creator.py
```

This will generate JSON and DOT files for your automaton.

### Advanced CLI (`tools/cli.py`)

Load and test automata from JSON or DOT files, or engage in step-by-step execution.

**Load from JSON and test:**

```bash
python tools/cli.py --load-from my_fsm.json
```

**Load from DOT file and test:**

```bash
python tools/cli.py --dot-file path/to/your/automaton.gv
```

### DOT File Customization (`tools/dot_customizer.py`)

Modify and render existing DOT graph files. For example, to highlight the initial state:

```bash
python tools/dot_customizer.py --input path/to/input.gv --output customized_automaton
```

This will generate `customized_automaton.dot` and `customized_automaton.png`.

## Future Work

The journey of `PyCompilerDesign` is continuous. We envision further enhancements to make the interaction with formal languages even more intuitive and powerful. Our roadmap includes:

-   **Regular Expression Integration:** **[DONE]** Seamless integration with regular expressions, allowing users to define automata directly from regex patterns and vice-versa.
-   **Minimization Algorithms:** Implement classic DFA minimization algorithms (e.g., Myhill-Nerode theorem, partition refinement) to optimize automata for efficiency and elegance.
-   **Advanced Visualization Features:** Explore dynamic visualization capabilities, such as animating state transitions during input processing, or generating interactive web-based visualizations.
-   **Formal Verification Tools:** Integrate tools for formal verification, enabling users to prove properties about their automata, suchs as equivalence or language inclusion.
-   **Context-Free Grammar (CFG) Support:** Extend the library to support more complex language models, potentially including pushdown automata and context-free grammars.
-   **Performance Optimization:** Continuously refine the underlying algorithms for enhanced performance, especially when dealing with very large or complex automata.
-   **Web-Based Interface:** Investigate the development of a user-friendly web interface, allowing for visual FSM design, simulation, and analysis directly in a browser.

## Challenges & Learnings

Developing `PyCompilerDesign` involved navigating several complex theoretical and practical challenges, including:

-   **Implementing Core Automata Logic:** Accurately translating mathematical definitions of DFAs and NFAs into robust Python code.
-   **Regular Expression Parsing:** Building a reliable mechanism to convert regex patterns into NFA structures.
-   **Graph Visualization Integration:** Seamlessly connecting Python code with Graphviz for clear and accurate visual representations of automata.
-   **Managing State Transitions:** Ensuring correct state management and transitions during automaton simulation.
-   **Performance Considerations:** Optimizing algorithms for efficiency, especially when dealing with larger automata or complex regex patterns.

This project significantly deepened my understanding of formal language theory, compiler design principles, and the practical application of graph theory in software development.

## Acknowledgments

This project builds upon the foundational work of **James Ansley** (GitHub: [James-Ansley](https://github.com/James-Ansley)) from the original `python-fsa` repository. His elegant design principles laid the groundwork for the advanced capabilities now present in `PyCompilerDesign`.

## Contact

MemaroX - [Your GitHub Profile Link](https://github.com/MemaroX)
