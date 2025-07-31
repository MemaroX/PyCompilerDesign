import pytest
from collections import deque
from main import CLI, EndOfInputError
import io
import sys

# Helper function to run a CLI method with a given input queue and capture output
def run_cli_method(cli_method, input_queue, capsys):
    """Runs a CLI method with a given input queue and captures the output."""
    original_input_queue = cli_method.__self__.input_queue
    cli_method.__self__.input_queue = deque(input_queue)
    
    try:
        cli_method()
    except EndOfInputError:
        # This is expected when the input queue is exhausted
        pass
    finally:
        # Restore original queue if necessary
        cli_method.__self__.input_queue = original_input_queue
        
    captured = capsys.readouterr()
    return captured.out

@pytest.fixture
def cli():
    """Provides a CLI instance for testing."""
    return CLI()

def test_lex_code(cli, capsys):
    """Tests the lex_code method."""
    inputs = ["let x = 10;", "END"]
    output = run_cli_method(cli.lex_code, inputs, capsys)
    assert "--- Tokens ---" in output
    # Check for the presence of token details in the output
    assert "Token(type=<TokenType.LET: 'let'>" in output
    assert "Token(type=<TokenType.IDENTIFIER: 'IDENTIFIER'>, value='x'" in output
    assert "--- Symbol Table ---" in output
    assert "x: {'line': 1, 'column': 5}" in output

def test_parse_code_success(cli, capsys):
    """Tests the parse_code method with valid code."""
    inputs = ["let x = 5 + 10;", "END"]
    output = run_cli_method(cli.parse_code, inputs, capsys)
    assert "--- AST ---" in output
    assert "Program" in output
    assert "VariableDeclaration" in output
    assert "BinaryOperation(LiteralExpression(5), '+', LiteralExpression(10))" in output

def test_parse_code_failure(cli, capsys):
    """Tests the parse_code method with invalid code to ensure error handling."""
    inputs = ["let x = ;", "END"]
    output = run_cli_method(cli.parse_code, inputs, capsys)
    assert "Parsing Error:" in output

def test_regex_to_nfa_dfa(cli, capsys):
    """Tests the regex_to_nfa_dfa method."""
    inputs = ["a|b"]
    output = run_cli_method(cli.regex_to_nfa_dfa, inputs, capsys)
    assert "--- NFA for 'a|b' ---" in output
    assert "--- Equivalent DFA ---" in output

def test_fsa_to_regex_conversion(cli, capsys):
    """Tests the fsa_to_regex_conversion method."""
    inputs = [
        "q0,q1",      # states
        "a,b",        # alphabet
        "q0",         # initial state
        "q1",         # final states
        "q0,a,q1"     # transitions
    ]
    output = run_cli_method(cli.fsa_to_regex_conversion, inputs, capsys)
    assert "--- FSA to Regex Conversion ---" in output
    assert "Converted Regex:" in output

def test_nfa_acceptance(cli, capsys):
    """Tests the test_nfa method."""
    inputs = [
        "a*",      # regex
        "aaa",     # should be accepted
        "aab",     # should be rejected
        "q"        # quit
    ]
    output = run_cli_method(cli.test_nfa, inputs, capsys)
    assert "'aaa' is ACCEPTED" in output
    assert "'aab' is REJECTED" in output

def test_minimize_dfa(cli, capsys):
    """Tests the minimize_dfa method."""
    inputs = ["(a|b)*abb"]
    output = run_cli_method(cli.minimize_dfa, inputs, capsys)
    assert "Original DFA" in output
    assert "Minimized DFA" in output
    assert "Original DFA saved to original_dfa.dot" in output
    assert "Minimized DFA saved to minimized_dfa.dot" in output

def test_semantic_analysis_success(cli, capsys):
    """Tests the analyze_code_semantic method with valid code."""
    inputs = ["let x = 10; let y = x;", "END"]
    output = run_cli_method(cli.analyze_code_semantic, inputs, capsys)
    assert "Semantic analysis completed successfully" in output

def test_semantic_analysis_failure(cli, capsys):
    """Tests the analyze_code_semantic method with a semantic error."""
    inputs = ["let x = y;", "END"]
    output = run_cli_method(cli.analyze_code_semantic, inputs, capsys)
    assert "Semantic Analysis Error: Undeclared variable" in output
    assert "'y'" in output

def test_ir_generation(cli, capsys):
    """Tests the generate_intermediate_code method."""
    inputs = ["let x = 10 + 20;", "END"]
    output = run_cli_method(cli.generate_intermediate_code, inputs, capsys)
    assert "Intermediate Code (Three-Address Code)" in output
    assert "t1" in output # Check for temporary variable
    assert "x = t1" in output

def test_code_optimization(cli, capsys):
    """Tests the optimize_code method."""
    inputs = [
        "let x = 10 + 20;",
        "let y = x;",
        "END"
    ]
    output = run_cli_method(cli.optimize_code, inputs, capsys)
    assert "Original Intermediate Code" in output
    assert "Optimized Intermediate Code" in output
    assert "Applied Optimizations:" in output
    assert "Constant Folding" in output or "Propagated constant" in output
    assert "Copy Propagation" in output or "Propagated constant" in output

def test_main_menu_exit(cli, capsys):
    """Tests that the main_menu exits correctly."""
    # Test exiting the main menu
    output = run_cli_method(cli.main_menu, ['10'], capsys)
    assert "Exiting PyCompilerDesign CLI. Goodbye!" in output

def test_main_menu_invalid_choice(cli, capsys):
    """Tests that the main_menu handles invalid choices."""
    # Test invalid choice
    output = run_cli_method(cli.main_menu, ['99', '10'], capsys)
    assert "Invalid choice. Please try again." in output
    assert "Exiting PyCompilerDesign CLI. Goodbye!" in output
