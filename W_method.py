from fsm import FSM
from intersection_fsm import FSM_Intersection
from collections import deque

class WMethod:
    def __init__(self, fsm: FSM):
        self.fsm = fsm

    def find_d_transfer_sequence(self, target_state):
        start_set = frozenset([self.fsm.start_state])
        queue = deque()
        queue.append( (start_set, []) )  

        visited = set()
        visited.add(start_set)

        while queue:
            current_set, path = queue.popleft()

            if current_set == frozenset([target_state]):
                return path

            for inp in self.fsm.alphabet:
                next_set = set()

                for state in current_set:
                    outs = self.fsm.transitions.get(state, {}).get(inp, [])
                    for _, nxt in outs:
                        next_set.add(nxt)

                if not next_set:
                    continue 

                next_set = frozenset(next_set)
                if next_set not in visited:
                    visited.add(next_set)
                    queue.append( (next_set, path + [inp]) )

        return None

    def compute_S(self):
        S = {self.fsm.start_state: []}
        for state in self.fsm.states:
            if state != self.fsm.start_state:
                path = self.find_d_transfer_sequence(state)
                if path is not None:
                    S[state] = path
        return S

    def compute_W(self):
        checked_pairs = set()
        distinguishing_sequences = {}

        for s1 in self.fsm.states:
            for s2 in self.fsm.states:
                if s1 != s2 and (s1, s2) not in checked_pairs:
                    transitions_dict = self.fsm.get_transitions() 
                    other_fsm = FSM(
                        states=self.fsm.states,
                        alphabet=self.fsm.alphabet,
                        output_alphabet=self.fsm.output_alphabet,
                        transitions=transitions_dict,
                        start_state=s2
                    )

                    inter = FSM_Intersection.intersection(self.fsm, other_fsm)
                    seqs = FSM_Intersection.find_seq(inter)
                    if seqs:
                        if seqs not in distinguishing_sequences.values():
                            distinguishing_sequences[(s1, s2)] = seqs
                    checked_pairs.add((s1, s2))
                    checked_pairs.add((s2, s1))

        return distinguishing_sequences

    def generate_test_suite(self):
        S = self.compute_S()
        S_sequences = list(S.values())
        print("Передаточные последовательности -", S_sequences)
        print("Алфавит -", self.fsm.alphabet)

        W_sequences = []
        W = self.compute_W()
        print(W)
        for _, sequences in W.items():
            for seq in sequences:
                if seq not in W_sequences:
                    W_sequences.append(seq)

        print("Различающие последовательности -", W_sequences)

        test_suite = set()
        for s in S_sequences:
            for i in self.fsm.alphabet:
                for w in W_sequences:
                    test_case = tuple(s + [i] + list(w))
                    test_suite.add(test_case)

        return sorted(test_suite, key=len)