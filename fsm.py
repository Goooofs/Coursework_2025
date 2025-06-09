class FSM:
    def __init__(self, states, alphabet, output_alphabet, transitions, start_state):
        self.states = states  
        self.alphabet = alphabet  
        self.output_alphabet = output_alphabet 
        self.transitions = transitions 
        self.start_state = start_state

    def get_transitions(self):
        return self.transitions

    def get_transitions_as_list(self):
        transition_list = []
        for from_state, inputs in self.transitions.items():
            for input_symbol, output_list in inputs.items():
                for output_symbol, to_state in output_list:
                    transition_list.append((from_state, input_symbol, output_symbol, to_state))
        return transition_list

    def get_states(self):
        return self.states

    def is_deterministic(self):
        for state in self.transitions:
            for input_symbol in self.transitions[state]:
                if len(self.transitions[state][input_symbol]) > 1:
                    return False  
        return True

    def print_info(self):
        print("FSM Information:")
        print("States:", self.states)
        print("Input Alphabet:", self.alphabet)
        print("Output Alphabet:", self.output_alphabet)
        print("Deterministic:", "Yes" if self.is_deterministic() else "No")
        print("Transitions:")
        for state in self.transitions:
            for input_symbol in self.transitions[state]:
                for output_symbol, to_state in self.transitions[state][input_symbol]:
                    print(f"  {state} --({input_symbol}/{output_symbol})--> {to_state}")
