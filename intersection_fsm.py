from fsm import FSM
from collections import deque

class FSM_Intersection:
    @staticmethod
    def intersection(fsm1, fsm2):
        if fsm1.alphabet != fsm2.alphabet:
            return None

        new_states = set()
        new_transitions = []
        output_alphabet = set(fsm1.output_alphabet).union(fsm2.output_alphabet)
        alphabet = fsm1.alphabet

        def transition_exist(fsm, state, symbol, output):
            for transition in fsm.get_transitions_as_list():
                if transition[:3] == (state, symbol, output):
                    return transition[3]
            return None

        def intersect(spec_state, impl_state):
            for symbol in alphabet:
                for output in output_alphabet:
                    new_spec_state = transition_exist(fsm1, spec_state, symbol, output)
                    new_impl_state = transition_exist(fsm2, impl_state, symbol, output)
                    if new_spec_state and new_impl_state is not None:
                        new_state = (spec_state, impl_state)
                        next_state = (new_spec_state, new_impl_state)

                        new_states.add(new_state)
                        new_states.add(next_state)

                        transition = (new_state, symbol, output, next_state)
                        if transition not in new_transitions:
                            new_transitions.append(transition)
                            intersect(new_spec_state, new_impl_state)

        intersect(fsm1.start_state, fsm2.start_state)

        transition_dict = {}
        for from_state, input_symbol, output_symbol, to_state in new_transitions:
            if from_state not in transition_dict:
                transition_dict[from_state] = {}
            if input_symbol not in transition_dict[from_state]:
                transition_dict[from_state][input_symbol] = []
            transition_dict[from_state][input_symbol].append((output_symbol, to_state))

        return FSM(states=new_states, alphabet=alphabet, output_alphabet=output_alphabet,
                   transitions=transition_dict, start_state=(fsm1.start_state, fsm2.start_state))

    @staticmethod
    def find_seq(fsm):
        def state_transitions(state):
            return [t for t in fsm.get_transitions_as_list() if t[0] == state]

        def indeterminate_state(transitions):
            symbols = [t[1] for t in transitions]
            return [s for s in fsm.alphabet if s not in symbols]

        def shortest_path(target_state):
            visited = set()
            queue = deque([(fsm.start_state, '')])
            reached_states = set()

            while queue:
                current_state, path = queue.popleft()
                if current_state == target_state:
                    reached_states.add(path)
                    continue
                visited.add(current_state)
                for t in state_transitions(current_state):
                    next_state, symbol = t[3], t[1]
                    if next_state not in visited:
                        queue.append((next_state, path + symbol))
            return reached_states

        list_seq = set()
        indeterminate_states = set()

        for t in fsm.get_transitions_as_list():
            transitions = state_transitions(t[3])
            flag = indeterminate_state(transitions)
            if flag:
                paths = shortest_path(t[3])
                for path in paths:
                    for i in flag:
                        list_seq.add(path + i)
                indeterminate_states.add(t[3])

        seq_states_dict = {}
        for seq in list_seq:
            current_states = {fsm.start_state}
            for symbol in seq[:-1]:
                next_states = set()
                for state in current_states:
                    for t in fsm.get_transitions_as_list():
                        if t[0] == state and t[1] == symbol:
                            next_states.add(t[3])
                if not next_states:
                    break
                current_states = next_states
            seq_states_dict[seq] = current_states

        valid_sequences = {seq for seq, states in seq_states_dict.items()
                           if all(s in indeterminate_states for s in states)}

        min_len = min((len(s) for s in valid_sequences), default=0)
        return sorted([s for s in valid_sequences if len(s) == min_len])

    @staticmethod
    def check_seq(fsm, input_sequence):
        paths = []

        def dfs(state, current_path, remaining):
            if not remaining:
                paths.append(current_path)
                return
            for t in fsm.get_transitions_as_list():
                if t[0] == state and (t[1] == remaining[0] or t[1] == ''):
                    next_state = t[3]
                    next_path = current_path + t[2]
                    dfs(next_state, next_path, remaining[1:] if t[1] == remaining[0] else remaining)

        dfs(fsm.start_state, '', input_sequence)
        return paths
