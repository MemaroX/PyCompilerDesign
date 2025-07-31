import pytest
from compiler.code_generator import CodeGenerator

@pytest.fixture
def code_gen():
    """Provides a CodeGenerator instance for testing."""
    return CodeGenerator()

def test_simple_arithmetic_generation(code_gen):
    """
    Tests the generation of assembly for simple arithmetic operations.
    """
    tac_instructions = [
        {'op': '+', 'arg1': '10', 'arg2': '20', 'result': 't1'},
        {'op': '*', 'arg1': 't1', 'arg2': '2', 'result': 't2'},
        {'op': '=', 'arg1': 't2', 'result': 'x'}
    ]
    
    assembly = code_gen.generate(tac_instructions)
    
    expected_assembly = [
        "LOAD R1, 10",
        "LOAD R2, 20",
        "ADD R3, R1, R2",  # t1 in R3
        "LOAD R4, 2",
        "MUL R5, R3, R4",  # t2 in R5
        "MOVE R6, R5",     # x in R6
        "STORE x, R6"
    ]
    
    assert assembly == expected_assembly

def test_variable_assignment(code_gen):
    """
    Tests code generation for variable assignments.
    """
    tac_instructions = [
        {'op': '=', 'arg1': '100', 'result': 'a'},
        {'op': '=', 'arg1': 'a', 'result': 'b'}
    ]
    
    assembly = code_gen.generate(tac_instructions)
    
    expected_assembly = [
        "LOAD R1, 100",  # a in R1
        "MOVE R2, R1",   # b in R2
        "STORE b, R2"
    ]
    
    assert assembly == expected_assembly

def test_no_instructions(code_gen):
    """
    Tests that an empty list of TAC instructions produces empty assembly.
    """
    assembly = code_gen.generate([])
    assert assembly == []
