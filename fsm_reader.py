from fsm import FSM
class FSMReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_info(self, transitions):
        """
        Извлекает состояния, алфавиты и выходные алфавиты из списка переходов.
        """
        states = set()
        alphabet = set()
        output_alphabet = set()

        for from_state, input_symbol, output_symbol, to_state in transitions:
            states.add(from_state)
            states.add(to_state)
            alphabet.add(input_symbol)
            output_alphabet.add(output_symbol)

        return list(states), list(alphabet), list(output_alphabet)

    def create_transition_dict(self, transitions):
        """
        Преобразует список переходов в словарь для удобства работы.
        """
        transition_dict = {}
        for from_state, input_symbol, output_symbol, to_state in transitions:
            if from_state not in transition_dict:
                transition_dict[from_state] = {}
            if input_symbol not in transition_dict[from_state]:
                transition_dict[from_state][input_symbol] = []
            transition_dict[from_state][input_symbol].append((output_symbol, to_state))
        return transition_dict

    def read_fsm(self):
        with open(self.file_path, 'r') as file:
            content = file.readlines()

        current_transitions = []
        start_state = None

        for line in content:
            line = line.strip()
            if line.startswith('F'):
                if current_transitions:
                    states, alphabet, output_alphabet = self.extract_info(current_transitions)
                    transition_dict = self.create_transition_dict(current_transitions)
                    fsm = FSM(states=states, alphabet=alphabet, output_alphabet=output_alphabet,
                              transitions=transition_dict, start_state=start_state)
                    return fsm  # Возвращаем только один автомат
                current_transitions = []
                start_state = None
            elif line.startswith('n0'):
                start_state = line.split(' ')[1]
            elif line.startswith(('s ', 'i ', 'o ', 'F ','p ')):
                continue
            elif line:
                transition = tuple(line.split(' '))
                current_transitions.append(transition)

        if current_transitions:
            states, alphabet, output_alphabet = self.extract_info(current_transitions)
            transition_dict = self.create_transition_dict(current_transitions)
            fsm = FSM(states=states, alphabet=alphabet, output_alphabet=output_alphabet,
                      transitions=transition_dict, start_state=start_state)
            return fsm
