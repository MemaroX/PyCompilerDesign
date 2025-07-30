import unittest
from compiler.fsa import DFA, NFA

class TestFSA(unittest.TestCase):

    def test_dfa_acceptance(self):
        dfa = DFA(
            states={'q0', 'q1', 'q2'},
            alphabet={'0', '1'},
            initial='q0',
            final={'q2'},
            transitions={('q0', '0'): 'q1', ('q1', '1'): 'q2'}
        )
        self.assertTrue(dfa.accepts(['0', '1']))
        self.assertFalse(dfa.accepts(['0', '0']))

    def test_nfa_acceptance(self):
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            alphabet={'a', 'b'},
            initial='q0',
            final={'q2'},
            transitions={('q0', 'a'): ['q1'], ('q1', 'b'): ['q2']}
        )
        self.assertTrue(nfa.accepts(['a', 'b']))
        self.assertFalse(nfa.accepts(['a', 'a']))

if __name__ == '__main__':
    unittest.main()