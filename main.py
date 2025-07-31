from compiler.fsa import parse_regex
from compiler.lexer.lexer import CppLexer
from compiler.parser import Parser
from compiler.ast_nodes import Program, Statement, Expression, LiteralExpression, BinaryOperation
from compiler.fsa_core import NFA, DFA
from compiler.fsa_minimizer import DFAMinimizer
from compiler.fsa_to_regex import FSAToRegexConverter
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.ir_generator import IRGenerator
from collections import deque
import traceback

class EndOfInputError(Exception):
    """Custom exception to signal the end of predefined input."""
    pass

class CLI:
    def __init__(self, input_queue=None):
        self.dfa_minimizer = DFAMinimizer()
        self.fsa_to_regex_converter = FSAToRegexConverter()
        self.input_queue = deque(input_queue) if input_queue else None

    def _get_input(self, prompt: str = "") -> str:
        if self.input_queue is not None:
            if len(self.input_queue) > 0:
                return self.input_queue.popleft()
            else:
                # If input_queue is exhausted, raise an error for non-interactive calls
                raise EndOfInputError("Predefined input queue is empty.")
        return input(prompt)

    def _get_multiline_input(self, prompt: str) -> str:
        print(prompt)
        code_lines = []
        while True:
            try:
                line = self._get_input()
                if line == 'END':
                    break
                code_lines.append(line)
            except EndOfInputError:
                break # Stop reading if input queue is exhausted
        return "\n".join(code_lines)

    def lex_code(self):
        code = self._get_multiline_input("Enter code to lex (type 'END' on a new line to finish):")
        lexer = CppLexer(code)
        tokens, symbol_table = lexer.tokenize_and_filter(include_comments=True, include_newlines=True)
        print("\n--- Tokens ---")
        for token in tokens:
            print(token)
        print("--------------\n")
        print("--- Symbol Table ---")
        for identifier, info in symbol_table.items():
            print(f"{identifier}: {info}")
        print("--------------------\n")

    def parse_code(self):
        code = self._get_multiline_input("Enter code to parse (type 'END' on a new line to finish):")
        lexer = CppLexer(code)
        tokens, _ = lexer.tokenize_and_filter(include_comments=False, include_newlines=False)
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            print("\n--- AST ---")
            # For now, a simple representation. We can enhance this later.
            print(ast)
            print("--------------\n")
        except ValueError as e:
            print(f"Parsing Error: {e}\n")

    def regex_to_nfa_dfa(self):
        regex_str = self._get_input("Enter a regular expression: ")
        try:
            regex_obj = parse_regex(regex_str)
            nfa = regex_obj.to_nfa()
            dfa = nfa.to_dfa()

            print(f"\n--- NFA for '{regex_str}' ---")
            print(f"Initial State: {nfa.initial}")
            print(f"Final States: {nfa.final}")
            print(f"Transitions: {nfa.transitions}")
            print("---------------------------\n")

            print(f"\n--- Equivalent DFA ---")
            print(f"Initial State: {dfa.initial}")
            print(f"Final States: {dfa.final}")
            print(f"Transitions: {dfa.transitions}")
            print("-----------------------\n")

        except Exception as e:
            print(f"Error in Regex to NFA/DFA conversion: {e}\n")
            traceback.print_exc() # Print full traceback

    def fsa_to_regex_conversion(self):
        print("\n--- FSA to Regex Conversion ---")
        print("Enter NFA/DFA details to convert to Regex.")
        print("Note: This is a simplified input for demonstration.")
        print("For complex FSAs, you might need to manually construct the NFA/DFA object.")

        try:
            states_str = self._get_input("Enter states (comma-separated, e.g., q0,q1): ")
            states = set(states_str.split(','))

            alphabet_str = self._get_input("Enter alphabet symbols (comma-separated, e.g., a,b): ")
            alphabet = set(alphabet_str.split(','))

            initial_state = self._get_input("Enter initial state: ")

            final_states_str = self._get_input("Enter final states (comma-separated): ")
            final_states = set(final_states_str.split(','))

            transitions_str = self._get_input("Enter transitions (from,symbol,to; from,symbol,to; ...): ")
            transitions_list = transitions_str.split(';')
            transitions = {}
            for t in transitions_list:
                if t.strip() == "": continue
                parts = t.strip().split(',')
                if len(parts) == 3:
                    from_state, symbol, to_state = parts
                    if (from_state, symbol) not in transitions:
                        transitions[(from_state, symbol)] = set()
                    transitions[(from_state, symbol)].add(to_state)
                else:
                    print(f"Invalid transition format: {t}. Skipping.")
                    continue
            
            nfa_transitions_frozenset = {}
            for (from_s, sym), to_s_set in transitions.items():
                nfa_transitions_frozenset[(from_s, sym)] = frozenset(to_s_set)

            input_nfa = NFA(
                states=frozenset(states),
                alphabet=frozenset(alphabet),
                initial=initial_state,
                transitions=nfa_transitions_frozenset,
                final=frozenset(final_states),
                epsilon=NFA.EPSILON
            )

            regex = self.fsa_to_regex_converter.convert_fsa_to_regex(input_nfa)
            print(f"\nConverted Regex: {regex}")
            print("---------------------------\n")

        except Exception as e:
            print(f"Error during FSA to Regex conversion: {e}\n")
            traceback.print_exc() # Print full traceback

    def test_nfa(self):
        regex_str = self._get_input("Enter the regex for the NFA to test: ")
        try:
            regex_obj = parse_regex(regex_str)
            nfa = regex_obj.to_nfa()
            while True:
                test_string = self._get_input("Enter string to test (or 'q' to quit): ")
                if test_string == 'q':
                    break
                test_chars = list(test_string)
                if nfa.accepts(test_chars):
                    print(f"'{test_string}' is ACCEPTED by the NFA.")
                else:
                    print(f"'{test_string}' is REJECTED by the NFA.")
            print("\n")
        except ValueError as e:
            print(f"NFA Test Error: {e}\n")
            traceback.print_exc() # Print full traceback

    def main_menu(self):
        while True:
            print("--- PyCompilerDesign CLI ---")
            print("1. Lex Code")
            print("2. Parse Code")
            print("3. Regex to NFA/DFA")
            print("4. Test NFA Acceptance (from Regex)")
            print("5. Convert FSA to Regex")
            print("6. Minimize DFA (from Regex)")
            print("7. Semantic Analysis")
            print("8. Intermediate Code Generation")
            print("9. Exit")
            
            try:
                choice = self._get_input("Enter your choice: ")
            except EndOfInputError:
                break # Exit gracefully if predefined input is exhausted

            if choice == '1':
                self.lex_code()
            elif choice == '2':
                self.parse_code()
            elif choice == '3':
                self.regex_to_nfa_dfa()
            elif choice == '4':
                self.test_nfa()
            elif choice == '5':
                self.fsa_to_regex_conversion()
            elif choice == '6':
                self.minimize_dfa()
            elif choice == '7':
                self.analyze_code_semantic()
            elif choice == '8':
                self.generate_intermediate_code()
            elif choice == '9':
                print("Exiting PyCompilerDesign CLI. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.\n")

    def generate_intermediate_code(self):
        code = self._get_multiline_input("Enter code for intermediate code generation (type 'END' on a new line to finish):")
        lexer = CppLexer(code)
        tokens, _ = lexer.tokenize_and_filter(include_comments=False, include_newlines=False)
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            # Perform semantic analysis before IR generation
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            ir_generator = IRGenerator()
            tac_instructions = ir_generator.generate(ast)

            print("\n--- Intermediate Code (Three-Address Code) ---")
            for i, tac in enumerate(tac_instructions):
                print(f"{i}: {tac}")
            print("----------------------------------------------\n")

        except ValueError as e:
            print(f"Error during intermediate code generation: {e}\n")
        except Exception as e:
            print(f"An unexpected error occurred during intermediate code generation: {e}\n")
            traceback.print_exc()

    def analyze_code_semantic(self):
        code = self._get_multiline_input("Enter code for semantic analysis (type 'END' on a new line to finish):")
        lexer = CppLexer(code)
        tokens, _ = lexer.tokenize_and_filter(include_comments=False, include_newlines=False)
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            print("\n--- Semantic Analysis Result ---")
            print("Semantic analysis completed successfully. No errors found.")
            print("----------------------------------\n")
        except ValueError as e:
            print(f"Semantic Analysis Error: {e}\n")
        except Exception as e:
            print(f"An unexpected error occurred during semantic analysis: {e}\n")
            traceback.print_exc()

    def minimize_dfa(self):
        regex_str = self._get_input("Enter a regular expression to create a DFA to minimize: ")
        try:
            regex_obj = parse_regex(regex_str)
            nfa = regex_obj.to_nfa()
            dfa = nfa.to_dfa()

            print(f"\n--- Original DFA (from regex '{regex_str}') ---")
            print(dfa)
            with open("original_dfa.dot", "w") as f:
                f.write(dfa.to_dot())
            print("Original DFA saved to original_dfa.dot")
            
            minimized_dfa = self.dfa_minimizer.minimize(dfa)

            print(f"\n--- Minimized DFA ---")
            print(minimized_dfa)
            with open("minimized_dfa.dot", "w") as f:
                f.write(minimized_dfa.to_dot())
            print("Minimized DFA saved to minimized_dfa.dot")
            print("-----------------------\n")

        except Exception as e:
            print(f"Error in DFA minimization: {e}\n")
            traceback.print_exc()

if __name__ == "__main__":
    cli = CLI(input_queue=[
        '8',
        'int x = 10; int y; y = 10 + 20;',
        'END',
        '9'
    ])
    cli.main_menu()