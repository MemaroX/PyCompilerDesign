# PyCompilerDesign: The Comprehensive Toolkit for Compiler Design and Formal Languages

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Unlocking the World of Compilers and Formal Languages

`PyCompilerDesign` is the definitive Python project designed to be your robust, intuitive, and complete toolkit for exploring, designing, and analyzing fundamental concepts in compiler design and formal language theory. This project serves as the **central reference and future development hub** for all compiler-related endeavors, providing a complete, end-to-end compiler implementation from source code to a target assembly-like language.

## Project Structure

```
PyCompilerDesign/
├── compiler/
│   ├── fsa/
│   ├── lexer/
│   ├── __init__.py
│   ├── ast_nodes.py
│   ├── code_generator.py
│   ├── fsa_core.py
│   ├── fsa_minimizer.py
│   ├── fsa_to_regex.py
│   ├── ir_generator.py
│   ├── lexer.py
│   ├── optimizer.py
│   ├── parser.py
│   └── semantic_analyzer.py
├── tests/
│   ├── __init__.py
│   ├── test_code_generator.py
│   ├── test_fsa_core.py
│   ├── test_fsa_minimizer.py
│   ├── test_fsa_to_regex.py
│   ├── test_fsa.py
│   ├── test_lexer.py
│   ├── test_main.py
│   ├── test_nfa_acceptance_core.py
│   └── test_parser.py
├── tools/
│   ├── cli.py
│   ├── dot_customizer.py
│   └── fsm_creator.py
├── main.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Key Features

-   **End-to-End Compiler Pipeline:** Implement and experiment with every phase of a modern compiler, from source code to target code:
    -   **Lexical Analysis:** A robust C++-oriented lexer that generates tokens and a symbol table.
    -   **Parsing:** A parser that constructs an Abstract Syntax Tree (AST) from the token stream.
    -   **Semantic Analysis:** A semantic analyzer that traverses the AST to find errors like undeclared variables.
    -   **Intermediate Code Generation:** An IR generator that produces Three-Address Code (TAC).
    -   **Code Optimization:** An optimizer that applies techniques like constant folding and copy propagation to the IR.
    -   **Code Generation:** A code generator that translates the optimized IR into a simple, human-readable assembly language.
-   **Comprehensive FSA Toolkit:** A complete suite of tools for working with Finite State Automata.
    -   **DFA & NFA Implementation:** Core classes for Deterministic and Nondeterministic Finite Automata.
    -   **Regex to NFA/DFA Conversion:** Seamlessly convert regular expressions into their equivalent automata.
    -   **DFA Minimization:** An efficient algorithm to produce the smallest possible equivalent DFA.
    -   **FSA to Regex Conversion:** Convert NFAs and DFAs back into regular expressions.
-   **Interactive CLI:** A powerful and user-friendly command-line interface, logically organized into "Compiler Phases" and "FSA Tools" for a clear and efficient workflow.
-   **Visualization:** Integration with Graphviz to transform abstract automata into clear visual diagrams.

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

Run the main application to access the interactive CLI.

```bash
python main.py
```

You will be presented with a menu to choose from various compiler and FSA functionalities:

```
--- PyCompilerDesign CLI ---

--- Compiler Phases ---
1. Lex Code
2. Parse Code
3. Semantic Analysis
4. Intermediate Code Generation
5. Code Optimization
6. Full Compilation (to Assembly)

--- FSA Tools ---
7. Regex to NFA/DFA
8. Test NFA Acceptance (from Regex)
9. Convert FSA to Regex
10. Minimize DFA (from Regex)

11. Exit
```

Follow the on-screen prompts to explore the different features.

## Testing

The project includes a comprehensive test suite to ensure the correctness and stability of all components. To run the tests, use `pytest`:

```bash
pytest
```

## Future Work

The journey of `PyCompilerDesign` is continuous. As the central reference for compiler design, its roadmap includes:

-   **Advanced Parsing Techniques:** Implement various parsing algorithms (e.g., LL(1), LR(1)) to handle more complex grammars.
-   **Target-Specific Code Generation:** Enhance the code generator to target real-world instruction sets (e.g., x86, ARM, or WebAssembly).
-   **Advanced Optimization:** Implement more sophisticated optimization techniques, such as loop optimizations or data-flow analysis.
-   **Web-Based Interface:** Investigate the development of a user-friendly web interface, allowing for visual compiler exploration and analysis directly in a browser.

## Acknowledgments

This project builds upon the foundational work of **James Ansley** (GitHub: [James-Ansley](https://github.com/James-Ansley)) from the original `python-fsa` repository. His elegant design principles laid the groundwork for the advanced capabilities now present in `PyCompilerDesign`.

## Contact

MemaroX - [Your GitHub Profile Link](https://github.com/MemaroX)
