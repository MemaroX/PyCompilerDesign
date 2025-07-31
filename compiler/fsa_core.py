from collections import defaultdict, deque
from collections.abc import Hashable, Iterable, Mapping
from pprint import pformat
from textwrap import indent
from typing import Final, Generic, Self, TypeVar

from compiler.fsa.fsa_utils import _closure_of, _closure_of_set, _flatten, _cull, _join

T = TypeVar("T", bound=Hashable)
S = TypeVar("S", bound=Hashable)
V = TypeVar("V", bound=Hashable)
Alphabet = frozenset[T]
States = frozenset[S]
Transitions = Mapping[tuple[S, T], frozenset[S]]


class DFA(Generic[T, S]):
    """
    Represents a Deterministic Finite Automaton (DFA).

    A DFA is defined by a set of states, an alphabet, a transition function,
    an initial state, and a set of final (accepting) states.
    """
    def __init__(
          self,
          *,
          alphabet: Iterable[T],
          states: Iterable[S],
          initial: S,
          transitions: Mapping[tuple[S, T], S],
          final: Iterable[S],
    ):
        """
        Initializes a DFA.

        Args:
            alphabet: The set of input symbols.
            states: The set of states in the DFA.
            initial: The initial state.
            transitions: A mapping from (state, symbol) pairs to the next state.
            final: A set of final (accepting) states.
        """
        self.alphabet: Final[Alphabet] = frozenset(alphabet)
        self.states: Final[States] = frozenset(states)
        self.initial: Final[S] = initial
        self.transitions: Final[Mapping[tuple[S, T], S]] = dict(transitions)
        self.final: Final[States] = frozenset(final)

    def accepts(self, input: Iterable[T]) -> bool:
        """
        Checks if the DFA accepts the given input string.

        Args:
            input: An iterable of symbols representing the input string.

        Returns:
            True if the input is accepted, False otherwise.
        """
        current = self.initial
        for e in input:
            current = self.transitions.get((current, e), None)
            if current is None:
                return False # No transition for the current symbol
        return current in self.final

    def squash(self) -> "DFA[T, str]":
        """
        Converts all states to strings.

        This is useful when wanting to render the DFA as a graph.

        Returns:
            A new DFA with all states converted to strings.
        """
        return DFA(
            alphabet=self.alphabet,
            states=(_join(state) for state in self.states),
            initial=_join(self.initial),
            transitions={
                (_join(from_), t): _join(to)
                for (from_, t), to in self.transitions.items()
            },
            final=(_join(state) for state in self.final),
        )

    def to_dot(self) -> str:
        """
        Converts the DFA to a DOT language string for visualization.

        Returns:
            A string in DOT format representing the DFA.
        """
        dot_lines = ["digraph DFA {", "    rankdir=LR;"]
        
        # Define states
        for state in self.states:
            shape = "doublecircle" if state in self.final else "circle"
            label = str(state)
            dot_lines.append(f'    "{label}" [shape={shape}];')
            
        # Define initial state
        dot_lines.append(f'    "" [shape=none];')
        dot_lines.append(f'    "" -> "{str(self.initial)}";')

        # Define transitions
        for (from_state, symbol), to_state in self.transitions.items():
            dot_lines.append(f'    "{str(from_state)}" -> "{str(to_state)}" [label="{str(symbol)}"];')
            
        dot_lines.append("}")
        return "\n".join(dot_lines)

    def __str__(self):
        return "\n".join((
            "DFA(",
            indent(f"alphabet={pformat(self.alphabet)},", " " * 4),
            indent(f"states={pformat(self.states)},", " " * 4),
            indent(f"initial={pformat(self.initial)},", " " * 4),
            indent(f"transitions={pformat(self.transitions)}", " " * 4),
            indent(f"final={pformat(self.final)},", " " * 4),
            ")",
        ))


class DFATransducer(Generic[T, S, V]):
    """
    A mutable Moore machine that accepts inputs one at a time.

    Allows for the DFA transitions to be a partial function – in the case a
    transition is not defined, the state and output become None, unless None
    is in the output domain.
    """
    def __init__(self, dfa: DFA[T, S], output: Mapping[S, V]):
        """
        Initializes a DFATransducer.

        Args:
            dfa: The DFA to transduce.
            output: A mapping from states to output values.
        """
        self._dfa = dfa
        self._output = output
        self._current = dfa.initial

    @property
    def current(self) -> S:
        """
        The current state of the transducer.
        """
        return self._current

    @property
    def output(self) -> V:
        """
        The current output of the transducer.
        """
        return self._output.get(self._current, None)

    @property
    def is_accepting(self) -> bool:
        """
        Returns True if the transducer is in an accepting state.
        """
        return self._current in self._dfa.final

    def push(self, input: T) -> V:
        """
        Transitions the transducer and returns the new output.

        Args:
            input: The input symbol to process.

        Returns:
            The output value of the new state.
        """
        self._current = self._dfa.transitions.get((self._current, input), None)
        return self.output


class NFA(Generic[T, S]):
    """
    Represents a Non-deterministic Finite Automaton (NFA).

    An NFA is defined by a set of states, an alphabet, a transition function,
    an initial state, a set of final (accepting) states, and an epsilon symbol.
    """
    EPSILON: Final[str] = "\u03B5"

    def __init__(
          self,
          *,
          states: Iterable[S],
          alphabet: Iterable[T],
          initial: S,
          transitions: Mapping[tuple[S, T], Iterable[S]],
          final: Iterable[S],
          epsilon: object = EPSILON,
    ):
        """
        Initializes an NFA.

        Args:
            states: The set of states in the NFA.
            alphabet: The set of input symbols.
            initial: The initial state.
            transitions: A mapping from (state, symbol) pairs to a set of next states.
            final: A set of final (accepting) states.
            epsilon: The symbol representing an epsilon transition.
        """
        self.states: Final[States] = frozenset(states)
        self.alphabet: Final[Alphabet] = frozenset(alphabet)
        self.initial: Final[S] = initial
        self.final: Final[States] = frozenset(final)
        self.epsilon: Final[object] = epsilon
        self.transitions: Final[Transitions] = {
            (s, t): frozenset(s1) for (s, t), s1 in transitions.items()
        }

    def accepts(self, input: Iterable[T]) -> bool:
        """
        Checks if the NFA accepts the given input string.

        Args:
            input: An iterable of symbols representing the input string.

        Returns:
            True if the input is accepted, False otherwise.
        """
        current_states = _closure_of(self.initial, self.transitions, self.epsilon)
        
        for symbol in input:
            next_states_after_input = set()
            for s in current_states:
                if (s, symbol) in self.transitions:
                    next_states_after_input.update(self.transitions[(s, symbol)])
            current_states = _closure_of_set(next_states_after_input, self.transitions, self.epsilon)

        return len(current_states.intersection(self.final)) > 0

    def to_dfa(self) -> DFA[T, frozenset[S]]:
        """
        Converts this NFA into an equivalent DFA using the subset construction algorithm.

        Returns:
            A new DFA that accepts the same language as this NFA.
        """
        # Re-compute flat transitions for DFA conversion
        closures = {s: _closure_of(s, self.transitions, self.epsilon) for s in self.states}
        _flat_initial = closures[self.initial]
        _flat_final = frozenset().union(*(closures[s] for s in self.final))
        _flat_transitions = _flatten(
            self.initial,
            self.states,
            self.transitions,
            closures,
            self.alphabet,
            self.epsilon,
        )

        new_transition = {}
        new_states = {_flat_initial}
        queue = deque(new_states)
        while queue:
            current = queue.pop()
            for elt in self.alphabet:
                s1 = frozenset().union(*(
                    _flat_transitions.get((s, elt), set())
                    for s in current
                ))
                if s1 and s1 not in new_states:
                    queue.append(s1)
                if s1:
                    new_transition[(current, elt)] = s1
                    new_states.add(s1)
        new_final = frozenset(
            s for s in new_states if len(s.intersection(_flat_final)) > 0
        )
        return DFA(
            alphabet=self.alphabet,
            states=frozenset(new_states),
            initial=_flat_initial,
            transitions=new_transition,
            final=new_final,
        )

    def without_epsilon(self) -> "NFA[T, S]":
        """
        Returns a new NFA with epsilon transitions removed.
        Any unreachable states as a result of this are also removed.

        Returns:
            A new NFA without epsilon transitions.
        """
        # This method will now use the re-computed flat transitions
        closures = {s: _closure_of(s, self.transitions, self.epsilon) for s in self.states}
        _flat_initial = closures[self.initial]
        _flat_final = frozenset().union(*(closures[s] for s in self.final))
        _flat_transitions = _flatten(
            self.initial,
            self.states,
            self.transitions,
            closures,
            self.alphabet,
            self.epsilon,
        )
        return NFA(
            alphabet=self.alphabet,
            states={s for (s, _) in _flat_transitions},
            initial=self.initial,
            transitions=_flat_transitions,
            final=self.final,
        )

    def transducer(
          self, output: Mapping[S, V] = None) -> "NFATransducer[T, S, V]":
        """
        Returns a transducer with the given output mapping.

        Args:
            output: A mapping from states to output values. If None,
                    this maps states to a boolean indicating whether the closure of that
                    state contains an accepting/final state.

        Returns:
            A new NFATransducer.
        """
        # This method will also use re-computed flat transitions
        closures = {s: _closure_of(s, self.transitions, self.epsilon) for s in self.states}
        _flat_initial = closures[self.initial]
        _flat_final = frozenset().union(*(closures[s] for s in self.final))
        _flat_transitions = _flatten(
            self.initial,
            self.states,
            self.transitions,
            closures,
            self.alphabet,
            self.epsilon,
        )
        if output is None:
            output = {s: s in _flat_final for s in self.states}
        return NFATransducer(
            _flat_initial,
            _flat_transitions,
            _flat_final,
            output,
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the NFA.
        """
        return "\n".join((
            "NFA(",
            indent(f"alphabet={pformat(self.alphabet)}", " " * 4),
            indent(f"states={pformat(self.states)}", " " * 4),
            indent(f"initial={pformat(self.initial)}", " " * 4),
            indent(f"transitions={pformat(self.transitions)}", " " * 4),
            indent(f"final={pformat(self.final)}", " " * 4),
            ")",
        ))


class NFATransducer(Generic[T, S, V]):
    """
    A mutable Moore machine that accepts inputs one at a time.

    The output of each "state" is the set of the mapping S -> V for all states, S, in the
    current state set.

    Allows for the NFA transitions to be a partial function – in the case a
    transition is not defined, the state and output become the empty set.
    """
    def __init__(
          self,
          initial: Iterable[S],
          transitions: Transitions,
          final: States,
          output: Mapping[S, V]
    ):
        """
        Initializes an NFATransducer.

        Args:
            initial: The initial state(s) of the transducer.
            transitions: The transition function of the underlying NFA.
            final: The set of final states of the underlying NFA.
            output: A mapping from states to output values.
        """
        self._current = frozenset(initial)
        self._transitions = transitions
        self._final = final
        self._output = output

    @property
    def current(self) -> frozenset[S]:
        """
        The current state set of the transducer.
        """
        return self._current

    @property
    def output(self) -> frozenset[V]:
        """
        The current output set of the transducer.
        """
        return frozenset(self._output[s] for s in self._current)

    @property
    def is_accepting(self) -> bool:
        """
        Returns True if the transducer is in an accepting state.
        """
        return len(self._current & self._final) != 0

    def push(self, input: T) -> frozenset[V]:
        """
        Transitions the transducer and returns the new output set.

        Args:
            input: The input symbol to process.

        Returns:
            The output set of the new state.
        """
        self._current = frozenset().union(
            *(self._transitions.get((s, input), set()) for s in self._current)
        )
        return self.output