import unittest
from compiler.fsa_core import NFA, DFA

class TestFSACore(unittest.TestCase):
    def test_nfa_acceptance(self):
        # Example NFA: accepts strings with an even number of 'a's
        nfa = NFA(
            states={'q0', 'q1'},
            alphabet={'a', 'b'},
            initial='q0',
            transitions={
                ('q0', 'a'): {'q1'},
                ('q0', 'b'): {'q0'},
                ('q1', 'a'): {'q0'},
                ('q1', 'b'): {'q1'},
            },
            final={'q0'}
        )
        self.assertTrue(nfa.accepts('aa'))
        self.assertFalse(nfa.accepts('bba'))
        self.assertFalse(nfa.accepts('a'))
        self.assertTrue(nfa.accepts('aba'))

    def test_nfa_to_dfa_conversion(self):
        # NFA that accepts (a|b)*abb
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            alphabet={'a', 'b'},
            initial='q0',
            transitions={
                ('q0', 'a'): {'q0', 'q1'},
                ('q0', 'b'): {'q0'},
                ('q1', 'b'): {'q2'},
                ('q2', 'b'): {'q3'},
            },
            final={'q3'}
        )
        dfa = nfa.to_dfa()

        # Test some strings
        self.assertTrue(dfa.accepts('abb'))
        self.assertTrue(dfa.accepts('aababb'))
        self.assertFalse(dfa.accepts('ab'))
        self.assertFalse(dfa.accepts('bba'))
        self.assertFalse(dfa.accepts('aabba'))

        # Test the type of the converted DFA
        self.assertIsInstance(dfa, DFA)
