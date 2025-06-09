import pygraphviz as pgv
import matplotlib.pyplot as plt
from collections import defaultdict

def visualize_FSM(fsm):
    G = pgv.AGraph(strict=False, directed=True)

    for state in fsm.states:
        G.add_node(str(state), shape='circle')
        if state == fsm.start_state:
            G.get_node(str(state)).attr['color'] = 'red'

    for state in fsm.transitions:
        for input_symbol in fsm.transitions[state]:
            for output_symbol, next_state in fsm.transitions[state][input_symbol]:
                label = f"{input_symbol}/{output_symbol}"
                G.add_edge(str(state), str(next_state), label=label)

    G.layout(prog='dot')
    G.draw("images/fsm.png", format='png')
    display_image("images/fsm.png")

def visualize_distinguishing_tree(state_tree, start_state):
    G = pgv.AGraph(directed=True, strict=False, rankdir="TB")
    G.node_attr.update(style='filled')

    for state in state_tree:
        if state != frozenset({'F'}):
            label = "{" + ",".join(sorted(state)) + "}"
        is_start = (state == start_state)
        has_transitions = bool(state_tree[state])

        if state == frozenset({'F'}):
            G.add_node("F", shape='doublecircle', fillcolor='#FF6666', penwidth=2, style='filled,bold', color='black')
        else:
            fill = '#90EE90' if is_start else ('white' if not has_transitions else 'lightgrey')
            G.add_node(label, fillcolor=fill)

    for state, transitions in state_tree.items():
        from_label = "F" if state == frozenset({'F'}) else "{" + ",".join(sorted(state)) + "}"
        f_transitions = [] 

        for _, io_trans in transitions.items():
            for io, next_state in io_trans:
                to_label = "F" if next_state == frozenset({'F'}) else "{" + ",".join(sorted(next_state)) + "}"
                if to_label == "F":
                    f_transitions.append(io)
                else:
                    G.add_edge(from_label, to_label, label=io, color='black')

        if f_transitions:
            G.add_edge(from_label, "F", label=", ".join(f_transitions), color='red')

    G.layout(prog='dot')
    G.draw("images/distinguishing_tree.png", format='png')
    display_image("images/distinguishing_tree.png")

def subset_label(B):
    if B == "F":
        return "F"

    if isinstance(B, str):
        return B

    if len(B) == 1:
        return next(iter(B))

    return "{" + ",".join(sorted(B)) + "}"

def visualize_ads(ads_paths, ads_builder, filename="images/ads.png"):
    nodes_seen = set()
    edge_labels = defaultdict(set)        

    for io_seq, _ in ads_paths:
        chain = ads_builder.trace_states(io_seq)
        for depth, (Bprev, Bnext) in enumerate(zip(chain[:-1], chain[1:])):
            u = subset_label(Bprev)
            v = subset_label(Bnext)
            i, o = io_seq[depth]
            edge_labels[(u, v)].add(f"{i}/{o}")
            nodes_seen.update([Bprev, Bnext])

    G = pgv.AGraph(strict=True, directed=True, rankdir="TB")
    G.node_attr.update(shape="box", style="rounded,filled", fontname="Arial")

    for B in nodes_seen:
        lbl = subset_label(B)

        is_inner = (not isinstance(B, str)) and B != "F" and len(B) > 1
        fill = "#CCCCCC" if is_inner else "white"

        G.add_node(lbl, fillcolor=fill)

    for (u, v), lbls in edge_labels.items():
        G.add_edge(u, v, label=", ".join(sorted(lbls)))

    G.layout(prog="dot")
    G.draw(filename, format="png")
    display_image(filename)

def display_image(filename):
    img = plt.imread(filename)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

