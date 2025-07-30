from collections import defaultdict
from compiler.fsa_core import NFA, DFA

class FSAToRegexConverter:
    def _concat_regex(self, r1: str, r2: str) -> str:
        if r1 == '∅' or r2 == '∅': return '∅'
        if r1 == NFA.EPSILON: return r2
        if r2 == NFA.EPSILON: return r1

        if '+' in r1 and not (r1.startswith('(') and r1.endswith(')')):
            r1 = f"({r1})"
        if '+' in r2 and not (r2.startswith('(') and r2.endswith(')')):
            r2 = f"({r2})"

        return r1 + r2

    def _union_regex(self, r1: str, r2: str) -> str:
        if r1 == '∅': return r2
        if r2 == '∅': return r1
        if r1 == r2: return r1
        return f"({r1}+{r2})"

    def _kleene_star_regex(self, r: str) -> str:
        if r == '∅': return NFA.EPSILON
        if r == NFA.EPSILON: return NFA.EPSILON
        
        if '+' in r or (len(r) > 1 and not (r.startswith('(') and r.endswith(')'))):
            return f"({r})*"
        return f"{r}*"

    def simplify_regex(self, regex_str: str) -> str:
        regex_str = regex_str.replace('∅+', '')
        regex_str = regex_str.replace('+∅', '')

        regex_str = regex_str.replace('∅', '')

        regex_str = regex_str.replace(NFA.EPSILON, '')

        regex_str = regex_str.replace(f'{NFA.EPSILON}*', '')
        regex_str = regex_str.replace(f'∅*', '')

        while '(((' in regex_str:
            regex_str = regex_str.replace('(((', '(')
        while ')))' in regex_str:
            regex_str = regex_str.replace(')))', ')')
        while '((' in regex_str:
            regex_str = regex_str.replace('((', '(')
        while '))' in regex_str:
            regex_str = regex_str.replace('))', ')')

        regex_str = regex_str.replace('()', '')

        while '++' in regex_str:
            regex_str = regex_str.replace('++', '+')

        if regex_str.startswith('+'):
            regex_str = regex_str[1:]
        if regex_str.endswith('+'):
            regex_str = regex_str[0:-1]

        return regex_str

    def convert_fsa_to_regex(self, fsa: NFA | DFA) -> str:
        if isinstance(fsa, DFA):
            nfa_states = set(fsa.states)
            nfa_alphabet = set(fsa.alphabet)
            nfa_initial = fsa.initial
            nfa_transitions = defaultdict(set)
            for (from_state, symbol), to_state in fsa.transitions.items():
                nfa_transitions[(from_state, symbol)].add(to_state)
            nfa_final = set(fsa.final)
            fsa = NFA(
                states=nfa_states,
                alphabet=nfa_alphabet,
                initial=nfa_initial,
                transitions=nfa_transitions,
                final=nfa_final,
                epsilon=''
            )

        new_start_state = "_S"
        new_end_state = "_F"

        transitions = defaultdict(lambda: defaultdict(lambda: '∅'))
        for (from_state, symbol), to_states in fsa.transitions.items():
            for to_state in to_states:
                if transitions[from_state][to_state] == '∅':
                    transitions[from_state][to_state] = str(symbol)
                else:
                    transitions[from_state][to_state] = self._union_regex(transitions[from_state][to_state], str(symbol))

        transitions[new_start_state][fsa.initial] = NFA.EPSILON

        for final_state in fsa.final:
            if transitions[final_state][new_end_state] == '∅':
                transitions[final_state][new_end_state] = NFA.EPSILON
            else:
                transitions[final_state][new_end_state] = self._union_regex(transitions[final_state][new_end_state], NFA.EPSILON)

        all_states = set(fsa.states) | {new_start_state, new_end_state}

        states_to_eliminate = sorted(list(all_states - {new_start_state, new_end_state}), key=str)

        for state_to_eliminate in states_to_eliminate:
            incoming_transitions = {}
            outgoing_transitions = {}
            self_loop = transitions[state_to_eliminate][state_to_eliminate]

            for i_state in all_states:
                if i_state == state_to_eliminate: continue
                if transitions[i_state][state_to_eliminate] != '∅':
                    incoming_transitions[i_state] = transitions[i_state][state_to_eliminate]

            for o_state in all_states:
                if o_state == state_to_eliminate: continue
                if transitions[state_to_eliminate][o_state] != '∅':
                    outgoing_transitions[o_state] = transitions[state_to_eliminate][o_state]

            all_states.remove(state_to_eliminate)

            for i_state, regex_in in incoming_transitions.items():
                for o_state, regex_out in outgoing_transitions.items():
                    path_regex = self._concat_regex(self._concat_regex(regex_in, self._kleene_star_regex(self_loop)), regex_out)

                    if transitions[i_state][o_state] == '∅':
                        transitions[i_state][o_state] = path_regex
                    else:
                        transitions[i_state][o_state] = self._union_regex(transitions[i_state][o_state], path_regex)

            for i_state in list(transitions.keys()):
                if i_state == state_to_eliminate:
                    del transitions[i_state]
                    continue
                for o_state in list(transitions[i_state].keys()):
                    if o_state == state_to_eliminate:
                        del transitions[i_state][o_state]

        final_regex = transitions[new_start_state][new_end_state]
        return self.simplify_regex(final_regex)
