from collections import defaultdict, deque
from collections.abc import Hashable, Iterable, Mapping
from functools import lru_cache
from typing import TypeVar

T = TypeVar("T", bound=Hashable)
S = TypeVar("S", bound=Hashable)
V = TypeVar("V", bound=Hashable)
Alphabet = frozenset[T]
States = frozenset[S]
Transitions = Mapping[tuple[S, T], frozenset[S]]

def _closure_of(state: S, transitions: Transitions, epsilon: object) -> States:
    """
    Computes the epsilon closure of a single state.

    Args:
        state: The state for which to compute the epsilon closure.
        transitions: The NFA's transition function.
        epsilon: The epsilon symbol.

    Returns:
        A frozenset of states representing the epsilon closure of the given state.
    """
    closure = {state}
    queue = deque(closure)
    while queue:
        current = queue.pop()
        next_ = transitions.get((current, epsilon), frozenset())
        queue.extend(next_ - closure)
        closure |= next_
    return frozenset(closure)

def _closure_of_set(states: Iterable[S], transitions: Transitions, epsilon: object) -> States:
    """
    Computes the epsilon closure of a set of states.

    Args:
        states: An iterable of states for which to compute the epsilon closure.
        transitions: The NFA's transition function.
        epsilon: The epsilon symbol.

    Returns:
        A frozenset of states representing the epsilon closure of the given set of states.
    """
    closure = set()
    for state in states:
        closure.update(_closure_of(state, transitions, epsilon))
    return frozenset(closure)


def _flatten(
      initial: S,
      states: States,
      transitions: Transitions,
      closures: Mapping[S, States],
      alphabet: Alphabet,
      epsilon: object,
) -> Transitions:
    """
    Flattens an NFA by removing epsilon transitions.

    Args:
        initial: The initial state of the NFA.
        states: The set of states in the NFA.
        transitions: The NFA's transition function.
        closures: A mapping of states to their epsilon closures.
        alphabet: The alphabet of the NFA.
        epsilon: The epsilon symbol.

    Returns:
        A new transition function for an equivalent NFA without epsilon transitions.
    """
    result = defaultdict(set)
    for q in states:
        for a in alphabet:
            target_states_after_a = set()
            for s in closures[q]:  # For each state in the epsilon closure of q
                if (s, a) in transitions: # If there's a transition from s on 'a'
                    target_states_after_a.update(transitions[(s, a)]) # Add all states reachable from s on 'a'
            
            final_target_states = set()
            for s_prime in target_states_after_a:
                final_target_states.update(closures[s_prime]) # Add the epsilon closure of s_prime

            if final_target_states:
                result[(q, a)] = frozenset(final_target_states)
    return _cull(
        initial,
        result
    )


def _cull(initial: S, transitions: Transitions) -> Transitions:
    """
    Removes unreachable states from a transition function.

    Args:
        initial: The initial state.
        transitions: The transition function.

    Returns:
        A new transition function with unreachable states removed.
    """
    reachable = {initial}
    queue = deque(reachable)
    while queue:
        current = queue.pop()
        next_reachable = set().union(*(s1 for (s, _), s1 in transitions.items() if s == current))
        queue.extend(next_reachable - reachable)
        reachable |= next_reachable
    return {(s, t): s1 for (s, t), s1 in transitions.items() if s in reachable}


def _join(elts: Iterable) -> str:
    """
    Joins elements of an iterable into a sorted string.

    Args:
        elts: The iterable of elements to join.

    Returns:
        A string representation of the joined elements.
    """
    if isinstance(elts, str):
        return elts
    elif isinstance(elts, Iterable):
        return "".join(sorted(str(e) for e in elts))
    else:
        return str(elts)
