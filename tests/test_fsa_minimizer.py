import unittest
from compiler.fsa_core import DFA
from compiler.fsa_minimizer import minimize_dfa

class TestFSAMinimizer(unittest.TestCase):
    def test_minimize_simple_dfa(self):
        # Example DFA from a common textbook (e.g., Sipser, Introduction to the Theory of Computation)
        # This DFA accepts strings ending in '01'
        dfa = DFA(
            states={'A', 'B', 'C', 'D', 'E', 'F'},
            alphabet={'0', '1'},
            initial='A',
            transitions={
                ('A', '0'): 'B', ('A', '1'): 'C',
                ('B', '0'): 'A', ('B', '1'): 'D',
                ('C', '0'): 'E', ('C', '1'): 'F',
                ('D', '0'): 'E', ('D', '1'): 'F',
                ('E', '0'): 'E', ('E', '1'): 'F',
                ('F', '0'): 'E', ('F', '1'): 'F',
            },
            final={'F'}
        )

        minimized_dfa = minimize_dfa(dfa)

        # Expected minimal DFA (states will be frozensets of original states)
        # The exact names of the frozensets will depend on the algorithm's grouping,
        # but the number of states and their behavior should be equivalent.
        # For this example, a minimal DFA should have 3 states.
        # {A, B}, {C, E}, {D, F}
        self.assertEqual(len(minimized_dfa.states), 3)

        # Test acceptance for some strings
        self.assertTrue(minimized_dfa.accepts('01'))
        self.assertTrue(minimized_dfa.accepts('101'))
        self.assertTrue(minimized_dfa.accepts('00101'))
        self.assertFalse(minimized_dfa.accepts('0'))
        self.assertFalse(minimized_dfa.accepts('1'))
        self.assertFalse(minimized_dfa.accepts('00'))
        self.assertFalse(minimized_dfa.accepts('10'))

    def test_minimize_already_minimal_dfa(self):
        # DFA that accepts strings containing an even number of 'a's
        dfa = DFA(
            states={'q0', 'q1'},
            alphabet={'a', 'b'},
            initial='q0',
            transitions={
                ('q0', 'a'): 'q1', ('q0', 'b'): 'q0',
                ('q1', 'a'): 'q0', ('q1', 'b'): 'q1',
            },
            final={'q0'}
        )

        minimized_dfa = minimize_dfa(dfa)
        self.assertEqual(len(minimized_dfa.states), 2)
        self.assertTrue(minimized_dfa.accepts('aa'))
        self.assertFalse(minimized_dfa.accepts('bba'))
        self.assertFalse(minimized_dfa.accepts('a'))

    def test_minimize_dfa_with_unreachable_states(self):
        # DFA with an unreachable state 'X'
        dfa = DFA(
            states={'A', 'B', 'C', 'X'},
            alphabet={'0', '1'},
            initial='A',
            transitions={
                ('A', '0'): 'B', ('A', '1'): 'C',
                ('B', '0'): 'B', ('B', '1'): 'C',
                ('C', '0'): 'C', ('C', '1'): 'C',
                ('X', '0'): 'X', ('X', '1'): 'X', # Unreachable state
            },
            final={'C'}
        )

        minimized_dfa = minimize_dfa(dfa)
        self.assertEqual(len(minimized_dfa.states), 3) # A, B, C should remain
        self.assertTrue(minimized_dfa.accepts('1'))
        self.assertTrue(minimized_dfa.accepts('01'))
        self.assertFalse(minimized_dfa.accepts('0'))
