from collections import defaultdict, deque
from compiler.fsa_core import DFA, States, Alphabet

class DFAMinimizer:
    def minimize(self, dfa: DFA) -> DFA:
        # Step 1: Remove unreachable states
        reachable_states = {dfa.initial}
        queue = deque([dfa.initial])
        while queue:
            current_state = queue.popleft()
            for symbol in dfa.alphabet:
                next_state = dfa.transitions.get((current_state, symbol))
                if next_state and next_state not in reachable_states:
                    reachable_states.add(next_state)
                    queue.append(next_state)

        # Filter transitions to only include reachable states
        filtered_transitions = {}
        for (from_state, symbol), to_state in dfa.transitions.items():
            if from_state in reachable_states and to_state in reachable_states:
                filtered_transitions[(from_state, symbol)] = to_state

        # Step 2: Initialize the distinguishability table
        distinguishable = defaultdict(lambda: defaultdict(bool))
        states_list = sorted(list(reachable_states), key=str) # Ensure consistent ordering
        n = len(states_list)

        for i in range(n):
            for j in range(i + 1, n):
                p, q = states_list[i], states_list[j]
                if (p in dfa.final and q not in dfa.final) or \
                   (p not in dfa.final and q in dfa.final):
                    distinguishable[p][q] = True
                    distinguishable[q][p] = True

        # Step 3: Iteratively mark distinguishable states
        changed = True
        while changed:
            changed = False
            for i in range(n):
                for j in range(i + 1, n):
                    p, q = states_list[i], states_list[j]
                    if not distinguishable[p][q]:
                        for symbol in dfa.alphabet:
                            next_p = filtered_transitions.get((p, symbol))
                            next_q = filtered_transitions.get((q, symbol))

                            if next_p is None and next_q is None:
                                continue
                            if next_p is None or next_q is None:
                                distinguishable[p][q] = True
                                distinguishable[q][p] = True
                                changed = True
                                break
                            if distinguishable[next_p][next_q]:
                                distinguishable[p][q] = True
                                distinguishable[q][p] = True
                                changed = True
                                break

        # Step 4: Group indistinguishable states
        new_states_map = {}
        new_states_list = []
        for state in reachable_states:
            if state not in new_states_map:
                new_group = {state}
                queue_group = deque([state])
                while queue_group:
                    current_group_state = queue_group.popleft()
                    for other_state in reachable_states:
                        if other_state not in new_states_map and not distinguishable[current_group_state][other_state]:
                            new_group.add(other_state)
                            queue_group.append(other_state)
                
                frozenset_group = frozenset(new_group)
                new_states_list.append(frozenset_group)
                for s in new_group:
                    new_states_map[s] = frozenset_group

        # Step 5: Construct the minimized DFA
        minimized_initial = new_states_map[dfa.initial]
        minimized_final = frozenset(new_states_map[s] for s in dfa.final if s in reachable_states)
        minimized_alphabet = dfa.alphabet
        minimized_states = frozenset(frozenset(group) for group in new_states_list)

        minimized_transitions = {}
        for (from_state, symbol), to_state in filtered_transitions.items():
            new_from_state = new_states_map[from_state]
            new_to_state = new_states_map[to_state]
            minimized_transitions[(new_from_state, symbol)] = new_to_state

        return DFA(
            alphabet=minimized_alphabet,
            states=minimized_states,
            initial=minimized_initial,
            transitions=minimized_transitions,
            final=minimized_final
        )