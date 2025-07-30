import unittest
from collections import defaultdict
from compiler.fsa_core import NFA, DFA, _closure_of

class TestNFAAcceptanceCore(unittest.TestCase):

    def test_closure_of_no_epsilon(self):
        transitions = {
            ('q0', 'a'): {'q1'},
            ('q1', 'b'): {'q2'},
        }
        # No epsilon transitions, so closure should be just the state itself
        self.assertEqual(_closure_of('q0', transitions, NFA.EPSILON), frozenset({'q0'}))
        self.assertEqual(_closure_of('q1', transitions, NFA.EPSILON), frozenset({'q1'}))

    def test_closure_of_simple_epsilon(self):
        transitions = {
            ('q0', NFA.EPSILON): {'q1'},
            ('q1', 'a'): {'q2'},
        }
        # q0 should close to {q0, q1}
        self.assertEqual(_closure_of('q0', transitions, NFA.EPSILON), frozenset({'q0', 'q1'}))
        self.assertEqual(_closure_of('q1', transitions, NFA.EPSILON), frozenset({'q1'}))

    def test_closure_of_chained_epsilon(self):
        transitions = {
            ('q0', NFA.EPSILON): {'q1'},
            ('q1', NFA.EPSILON): {'q2'},
            ('q2', 'a'): {'q3'},
        }
        # q0 should close to {q0, q1, q2}
        self.assertEqual(_closure_of('q0', transitions, NFA.EPSILON), frozenset({'q0', 'q1', 'q2'}))

    def test_closure_of_cycle_epsilon(self):
        transitions = {
            ('q0', NFA.EPSILON): {'q1'},
            ('q1', NFA.EPSILON): {'q0'},
        }
        # q0 should close to {q0, q1}
        self.assertEqual(_closure_of('q0', transitions, NFA.EPSILON), frozenset({'q0', 'q1'}))

    def test_nfa_accepts_simple(self):
        # NFA for 'a'
        nfa = NFA(
            states={'q0', 'q1'},
            alphabet={'a'},
            initial='q0',
            transitions={
                ('q0', 'a'): {'q1'}
            },
            final={'q1'},
            epsilon=NFA.EPSILON
        )
        self.assertTrue(nfa.accepts('a'))
        self.assertFalse(nfa.accepts('b'))
        self.assertFalse(nfa.accepts(''))

    def test_nfa_accepts_epsilon_transition(self):
        # NFA for 'a' with epsilon transition
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            alphabet={'a'},
            initial='q0',
            transitions={
                ('q0', NFA.EPSILON): {'q1'},
                ('q1', 'a'): {'q2'}
            },
            final={'q2'},
            epsilon=NFA.EPSILON
        )
        self.assertTrue(nfa.accepts('a'))
        self.assertFalse(nfa.accepts(''))

    def test_nfa_accepts_kleene_star_empty_string(self):
        # NFA for 'a*' (accepts empty string)
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            alphabet={'a'},
            initial='q0',
            transitions={
                ('q0', NFA.EPSILON): {'q1', 'q2'},
                ('q1', 'a'): {'q1'},
                ('q1', NFA.EPSILON): {'q2'}
            },
            final={'q2'},
            epsilon=NFA.EPSILON
        )
        self.assertTrue(nfa.accepts(''))
        self.assertTrue(nfa.accepts('a'))
        self.assertTrue(nfa.accepts('aa'))
        self.assertFalse(nfa.accepts('b'))

    def test_nfa_accepts_alternation(self):
        # NFA for 'a|b'
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5'},
            alphabet={'a', 'b'},
            initial='q0',
            transitions={
                ('q0', NFA.EPSILON): {'q1', 'q3'},
                ('q1', 'a'): {'q2'},
                ('q3', 'b'): {'q4'},
                ('q2', NFA.EPSILON): {'q5'},
                ('q4', NFA.EPSILON): {'q5'},
            },
            final={'q5'},
            epsilon=NFA.EPSILON
        )
        self.assertTrue(nfa.accepts('a'))
        self.assertTrue(nfa.accepts('b'))
        self.assertFalse(nfa.accepts('c'))
        self.assertFalse(nfa.accepts(''))

    def test_nfa_accepts_concatenation(self):
        # NFA for 'ab'
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            alphabet={'a', 'b'},
            initial='q0',
            transitions={
                ('q0', 'a'): {'q1'},
                ('q1', NFA.EPSILON): {'q2'},
                ('q2', 'b'): {'q3'},
            },
            final={'q3'},
            epsilon=NFA.EPSILON
        )
        self.assertTrue(nfa.accepts('ab'))
        self.assertFalse(nfa.accepts('a'))
        self.assertFalse(nfa.accepts('b'))
        self.assertFalse(nfa.accepts(''))
