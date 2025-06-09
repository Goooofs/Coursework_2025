from collections import defaultdict, deque
from copy import deepcopy
from itertools import product

from collections import deque, defaultdict
from copy import deepcopy

class Sdist:
    def __init__(self, fsm):
        self.fsm             = fsm
        self.transitions     = fsm.get_transitions()
        self.alphabet        = fsm.alphabet
        self.output_alphabet = fsm.output_alphabet
        self.start_state     = frozenset(fsm.states)
        self.F_state         = frozenset({"F"})

    def build(self, keep_singletons=False):

        tree    = {}
        visited = set()
        queue   = deque([self.start_state])        

        while queue:
            B = queue.popleft()
            if B in visited:
                continue
            visited.add(B)
            tree[B] = {}

            for inp in self.alphabet:

                by_state   = {}                   
                by_output  = defaultdict(set)    

                for s in B:
                    trs = self.transitions.get(s, {}).get(inp, [])
                    by_state[s] = set(trs)
                    for out, nxt in trs:
                        by_output[out].add(nxt)

                merge_happens = False
                states = list(B)
                for a in range(len(states)):
                    for b in range(a + 1, len(states)):
                        if by_state[states[a]] & by_state[states[b]]:
                            merge_happens = True
                            break
                    if merge_happens:
                        break

                if merge_happens:
                    for out in by_output:
                        label = f"{inp}/{out}"
                        tree[B].setdefault(inp, []).append((label, self.F_state))
                    continue      
                
                edges = []
                for out, next_set in by_output.items():
                    B_next = frozenset(next_set)
                    if len(B_next) > 1 or keep_singletons:
                        label = f"{inp}/{out}"
                        edges.append((label, B_next))
                        if B_next not in visited and len(B_next) > 1:
                            queue.append(B_next)

                if edges:                       
                    tree[B][inp] = edges

        return tree

    def readable_tree_output(self, tree):

        lines = []                            


        for B, trans_by_input in tree.items():

            B_label = "{ " + ", ".join(sorted(B, key=str)) + " }"

            for inp, edge_list in trans_by_input.items():

                for edge_label, B_next in edge_list:

                    B_next_label = "{ " + ", ".join(sorted(B_next, key=str)) + " }"

                    line = f"State {B_label} --({edge_label})--> {B_next_label}"
                    lines.append(line)

        return "\n".join(lines)

class ADSBuilder:
    def __init__(self, sdist, L: int | None = None) -> None:
        self.sdist = sdist
        self.alphabet = sdist.alphabet
        self.output_alphabet = sdist.output_alphabet
        self.start_state = frozenset(sdist.start_state)
        self.F = sdist.F_state

        self.full_tree = sdist.build(keep_singletons=True)
        self.tree_no_singletons = sdist.build(keep_singletons=False)

        self.L = L  
        self.UN: dict[frozenset, str] = {} 
        
        self.orig_cache: dict[tuple, set[str]] = {} 

    def compute_UN(self):
        tree = {}
        for state, trans in self.tree_no_singletons.items():
            inner = {}
            for inp, lst in trans.items():
                inner[inp] = list(lst)   
            tree[state] = inner

        incoming = {}
        for parent, trans in tree.items():
            for inp, lst in trans.items():
                for label, child in lst:
                    if child == self.F:
                        continue         
                    if child not in incoming:
                        incoming[child] = []
                    incoming[child].append((parent, inp))

        self.UN = {}
        queue = []
        for state in list(tree.keys()):
            for inp in self.alphabet:
                if inp not in tree.get(state, {}):  
                    self.UN[state] = inp
                    queue.append(state)
                    break   

        # 4) всплываем вверх
        while queue:
            bad = queue.pop(0)   
            if bad in tree:   
                del tree[bad]

            for parent, inp in incoming.get(bad, []):
                if parent not in tree:
                    continue

                new_edges = []
                for label, dst in tree[parent][inp]:
                    if dst != bad:
                        new_edges.append((label, dst))
                if new_edges:
                    tree[parent][inp] = new_edges
                else:
                    del tree[parent][inp]

                if parent not in self.UN and inp not in tree[parent]:
                    self.UN[parent] = inp
                    queue.append(parent)

    def orig_set_for_path(self, io_path):

        fsm = self.sdist.fsm

        good_orig = set()
        for s0 in self.start_state:
            curr = {s0} 

            ok = True
            for inp, out in io_path:
                nxt = set()
                for s in curr:
                    for o, ns in fsm.transitions[s][inp]:
                        if o == out:
                            nxt.add(ns)
                if not nxt:         
                    ok = False
                    break
                curr = nxt
            if ok:             
                good_orig.add(s0)

        return good_orig

    def expand(self, B, path, depth=0):
        if self.L is not None and depth >= self.L:
            return [(path, "F")]

        result = []           

        i = self.UN[B]

        for o in self.output_alphabet:
            label = f"{i}/{o}"

            next_state = None
            for lbl, dst in self.full_tree[B].get(i, []):
                if lbl == label:
                    next_state = dst
                    break

            if next_state is None:
                result.append((path + [(i, o)], "deadlock"))

            elif len(next_state) == 1 or next_state == self.F or next_state not in self.UN:
                full_path = path + [(i, o)]
                key = tuple(full_path)

                candidates = self.orig_cache.get(key)
                if candidates is None:
                    candidates = self.orig_set_for_path(full_path)
                    self.orig_cache[key] = candidates

                if len(candidates) == 1:
                    leaf = next(iter(candidates))
                else: 
                    leaf = ("{" + ",".join(sorted(next_state)) + "}"
                            if next_state != self.F else "F")

                result.append((full_path, leaf))

            else:
                deeper_paths = self.expand(next_state, path + [(i, o)], depth + 1)
                result.extend(deeper_paths)

        return result

    def build_test_example(self):
        self.compute_UN()
        if self.start_state not in self.UN:
            raise ValueError(
                "В начальном подмножестве нет неопределённого входа — "
                "ADS не существует."
            )
        return list(self.expand(self.start_state, []))

    def trace_states(self, io_path):
        chain   = []
        current = self.start_state
        chain.append(current)

        for inp, out in io_path:
            label_needed = f"{inp}/{out}"

            next_state = None
            for label, dst in self.full_tree[current][inp]:
                if label == label_needed:
                    next_state = dst
                    break

            current = next_state
            chain.append(current)

        key = tuple(io_path)
        cand = self.orig_cache.get(key)              
        if cand is not None and len(cand) == 1:
            chain[-1] = next(iter(cand))

        return chain

    def readable_test(self, ads_paths, show_states=False):
        result_lines = []

        for io_seq, leaf in ads_paths:

            pairs_txt = []
            for i, o in io_seq:
                pairs_txt.append(f"{i}/{o}")
            io_str = "  ".join(pairs_txt)

            if show_states:
                chain = self.trace_states(io_seq)

                chain_txt = []
                for B in chain:
                    if isinstance(B, str):
                        chain_txt.append(B)                   
                    elif B == self.F:
                        chain_txt.append("F")
                    else:
                        chain_txt.append("{" + ",".join(sorted(B)) + "}")

                states_str = " → ".join(chain_txt)
                line = f"{io_str:<13} | {states_str}"
            else:
                line = f"{io_str:<13} → {leaf}"

            result_lines.append(line)

        return "\n".join(result_lines)
