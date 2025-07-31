from collections.abc import Hashable, Iterable
from typing import Final, Generic, TypeVar

from compiler.fsa_core import NFA

T = TypeVar("T", bound=Hashable)
S = TypeVar("S", bound=Hashable)

class Regex(Generic[T]):
    def to_nfa(self) -> NFA[T, int]:
        raise NotImplementedError

class Literal(Regex[T]):
    def __init__(self, char: T):
        self.char = char

    def to_nfa(self) -> NFA[T, int]:
        # NFA for a single character 'c':
        # (0) --c--> (1)
        # initial state 0, final state 1
        return NFA(
            states={0, 1},
            alphabet={self.char},
            initial=0,
            transitions={(0, self.char): {1}},
            final={1},
            epsilon=NFA.EPSILON
        )

    def __repr__(self):
        return f"Literal('{self.char}')"

class Concatenation(Regex[T]):
    def __init__(self, regex1: Regex[T], regex2: Regex[T]):
        self.regex1 = regex1
        self.regex2 = regex2

    def to_nfa(self) -> NFA[T, int]:
        nfa1 = self.regex1.to_nfa()
        nfa2 = self.regex2.to_nfa()

        # Concatenation of NFA1 and NFA2:
        # Connect final states of NFA1 to initial state of NFA2 with epsilon transitions.
        # New initial state is NFA1's initial.
        # New final states are NFA2's final states.

        # Offset states of nfa2 to avoid conflicts
        offset = max(nfa1.states) + 1
        nfa2_states_offset = {s + offset for s in nfa2.states}
        nfa2_initial_offset = nfa2.initial + offset
        nfa2_final_offset = {s + offset for s in nfa2.final}

        new_transitions = {}
        # Add transitions from nfa1
        for (s, t), next_states in nfa1.transitions.items():
            new_transitions[(s, t)] = next_states
        # Add transitions from nfa2 (offset)
        for (s, t), next_states in nfa2.transitions.items():
            new_transitions[(s + offset, t)] = {ns + offset for ns in next_states}

        # Add epsilon transitions from final states of nfa1 to initial state of nfa2
        for final_state_nfa1 in nfa1.final:
            if (final_state_nfa1, NFA.EPSILON) in new_transitions:
                new_transitions[(final_state_nfa1, NFA.EPSILON)].add(nfa2_initial_offset)
            else:
                new_transitions[(final_state_nfa1, NFA.EPSILON)] = {nfa2_initial_offset}

        return NFA(
            states=nfa1.states.union(nfa2_states_offset),
            alphabet=nfa1.alphabet.union(nfa2.alphabet),
            initial=nfa1.initial,
            transitions=new_transitions,
            final=nfa2_final_offset,
            epsilon=NFA.EPSILON
        )

    def __repr__(self):
        return f"Concatenation({self.regex1!r}, {self.regex2!r})"

class Alternation(Regex[T]):
    def __init__(self, regex1: Regex[T], regex2: Regex[T]):
        self.regex1 = regex1
        self.regex2 = regex2

    def to_nfa(self) -> NFA[T, int]:
        nfa1 = self.regex1.to_nfa()
        nfa2 = self.regex2.to_nfa()

        # Alternation of NFA1 and NFA2:
        # Create new initial and final states.
        # Epsilon transitions from new initial to NFA1's and NFA2's initials.
        # Epsilon transitions from NFA1's and NFA2's finals to new final.

        new_initial = 0
        offset1 = 1
        offset2 = max(nfa1.states) + offset1 + 1
        new_final = max(nfa2.states) + offset2 + 1

        nfa1_states_offset = {s + offset1 for s in nfa1.states}
        nfa1_initial_offset = nfa1.initial + offset1
        nfa1_final_offset = {s + offset1 for s in nfa1.final}

        nfa2_states_offset = {s + offset2 for s in nfa2.states}
        nfa2_initial_offset = nfa2.initial + offset2
        nfa2_final_offset = {s + offset2 for s in nfa2.final}

        new_transitions = {}
        # Add transitions from nfa1 (offset)
        for (s, t), next_states in nfa1.transitions.items():
            new_transitions[(s + offset1, t)] = {ns + offset1 for ns in next_states}
        # Add transitions from nfa2 (offset)
        for (s, t), next_states in nfa2.transitions.items():
            new_transitions[(s + offset2, t)] = {ns + offset2 for ns in next_states}

        # Epsilon transitions from new_initial
        new_transitions[(new_initial, NFA.EPSILON)] = {nfa1_initial_offset, nfa2_initial_offset}

        # Epsilon transitions to new_final
        for final_state_nfa1 in nfa1_final_offset:
            if (final_state_nfa1, NFA.EPSILON) in new_transitions:
                new_transitions[(final_state_nfa1, NFA.EPSILON)].add(new_final)
            else:
                new_transitions[(final_state_nfa1, NFA.EPSILON)] = {new_final}
        for final_state_nfa2 in nfa2_final_offset:
            if (final_state_nfa2, NFA.EPSILON) in new_transitions:
                new_transitions[(final_state_nfa2, NFA.EPSILON)].add(new_final)
            else:
                new_transitions[(final_state_nfa2, NFA.EPSILON)] = {new_final}

        return NFA(
            states={new_initial, new_final}.union(nfa1_states_offset).union(nfa2_states_offset),
            alphabet=nfa1.alphabet.union(nfa2.alphabet),
            initial=new_initial,
            transitions=new_transitions,
            final={new_final},
            epsilon=NFA.EPSILON
        )

    def __repr__(self):
        return f"Alternation({self.regex1!r}, {self.regex2!r})"

class KleeneStar(Regex[T]):
    def __init__(self, regex: Regex[T]):
        self.regex = regex

    def to_nfa(self) -> NFA[T, int]:
        nfa = self.regex.to_nfa()

        # Kleene Star of NFA:
        # Create new initial and final states.
        # Epsilon transition from new initial to NFA's initial.
        # Epsilon transition from NFA's final to new final.
        # Epsilon transition from NFA's final to NFA's initial (for repetition).
        # Epsilon transition from new initial to new final (for zero occurrences).

        new_initial = 0
        offset = 1
        new_final = max(nfa.states) + offset + 1

        nfa_states_offset = {s + offset for s in nfa.states}
        nfa_initial_offset = nfa.initial + offset
        nfa_final_offset = {s + offset for s in nfa.final}

        new_transitions = {}
        # Add transitions from nfa (offset)
        for (s, t), next_states in nfa.transitions.items():
            new_transitions[(s + offset, t)] = {ns + offset for ns in next_states}

        # Epsilon transition from new_initial to nfa_initial_offset
        new_transitions[(new_initial, NFA.EPSILON)] = {nfa_initial_offset}

        # Epsilon transition from nfa_final_offset to new_final
        for final_state_nfa in nfa_final_offset:
            if (final_state_nfa, NFA.EPSILON) in new_transitions:
                new_transitions[(final_state_nfa, NFA.EPSILON)].add(new_final)
            else:
                new_transitions[(final_state_nfa, NFA.EPSILON)] = {new_final}

            # Epsilon transition from nfa_final_offset to nfa_initial_offset (for repetition)
            new_transitions[(final_state_nfa, NFA.EPSILON)].add(nfa_initial_offset)

        # Epsilon transition from new_initial to new_final (for zero occurrences)
        new_transitions[(new_initial, NFA.EPSILON)].add(new_final)

        return NFA(
            states={new_initial, new_final}.union(nfa_states_offset),
            alphabet=nfa.alphabet,
            initial=new_initial,
            transitions=new_transitions,
            final={new_final},
            epsilon=NFA.EPSILON
        )

    def __repr__(self):
        return f"KleeneStar({self.regex!r})"

def parse_regex(regex_str: str) -> Regex[str]:
    i = 0
    def peek():
        return regex_str[i] if i < len(regex_str) else None

    def consume(expected_char: str):
        nonlocal i
        if peek() == expected_char:
            i += 1
        else:
            raise ValueError(f"Expected '{expected_char}' but got '{peek()}'")

    def parse_atom():
        nonlocal i
        if peek() == '(':
            consume('(')
            regex = parse_expression()
            consume(')')
            return regex
        elif peek() is not None and peek().isalnum():
            char = peek()
            consume(char)
            return Literal(char)
        else:
            raise ValueError("Invalid regex atom")

    def parse_factor():
        nonlocal i
        atom = parse_atom()
        if peek() == '*':
            consume('*')
            return KleeneStar(atom)
        return atom

    def parse_term():
        nonlocal i
        term = parse_factor()
        while peek() is not None and peek() not in ['|', ')']:
            # Implicit concatenation
            factor = parse_factor()
            term = Concatenation(term, factor)
        return term

    def parse_expression():
        nonlocal i
        expression = parse_term()
        while peek() == '|':
            consume('|')
            term = parse_term()
            expression = Alternation(expression, term)
        return expression

    regex = parse_expression()
    if i != len(regex_str):
        raise ValueError("Unexpected characters at end of regex string")
    return regex