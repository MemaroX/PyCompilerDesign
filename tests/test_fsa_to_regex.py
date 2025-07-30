import unittest
from compiler.fsa_core import NFA, DFA
from compiler.fsa_to_regex import convert_fsa_to_regex

class TestFSAToRegex(unittest.TestCase):
    def test_simple_nfa_to_regex(self):
        # NFA that accepts 'a'
        nfa = NFA(
            states={'q0', 'q1'},
            alphabet={'a'},
            initial='q0',
            transitions={
                ('q0', 'a'): {'q1'}
            },
            final={'q1'}
        )
        regex = convert_fsa_to_regex(nfa)
        print(f"Generated Regex (simple): {regex}")
        self.assertEqual(regex, 'a')

    def test_nfa_with_epsilon_to_regex(self):
        # NFA that accepts 'a' using epsilon transition
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            alphabet={'a'},
            initial='q0',
            transitions={
                ('q0', NFA.EPSILON): {'q1'},
                ('q1', 'a'): {'q2'}
            },
            final={'q2'}
        )
        regex = convert_fsa_to_regex(nfa)
        self.assertEqual(regex, 'a')

    def test_dfa_to_regex(self):
        # DFA that accepts 'a'
        dfa = DFA(
            states={'q0', 'q1'},
            alphabet={'a'},
            initial='q0',
            transitions={
                ('q0', 'a'): 'q1'
            },
            final={'q1'}
        )
        regex = convert_fsa_to_regex(dfa)
        print(f"Generated Regex: {regex}")
        self.assertEqual(regex, 'a')
