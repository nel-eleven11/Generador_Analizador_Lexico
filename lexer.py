import pickle
import json


class Node:
    def __init__(self, state_id, is_accepting=False, token_ids=None):
        self.state_id = state_id
        self.transitions = {}
        self.is_accepting = is_accepting
        self.token_ids = token_ids if token_ids else []

    def add_transition(self, char, node):
        self.transitions[char] = node

    def get_next_node(self, char):
        return self.transitions.get(char)

    def __str__(self):
        return f"Node({self.state_id}, accepting={self.is_accepting}, tokens={self.token_ids})"


def load_dfa(transitions_file, acceptance_file):
    with open(transitions_file, 'rb') as f:
        transitions = pickle.load(f)
    with open(acceptance_file, 'rb') as f:
        acceptance = pickle.load(f)
    return transitions, acceptance


def build_dfa_nodes(transitions, acceptance):
    nodes = {}
    for state_id in transitions.keys():
        is_accepting = state_id in acceptance
        token_ids = acceptance.get(state_id, [])
        nodes[state_id] = Node(state_id, is_accepting, token_ids)

    for state_id, trans_dict in transitions.items():
        current_node = nodes[state_id]
        for char, next_state_id in trans_dict['transitions'].items():
            next_node = nodes[next_state_id]
            current_node.add_transition(char, next_node)

    return nodes, nodes[0]


def load_token_names(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return {token['id']: token['nombre'] for token in data['tokens']}


def lexical_analyzer(input_string, start_node, token_names):
    tokens = []
    current_position = 0

    with open('log.txt', 'w') as log_file:
        while current_position < len(input_string):
            current_node = start_node
            pos = current_position
            last_accepting_node = None
            last_accepting_pos = None
            selected_token_id = None

            while pos < len(input_string):
                char = input_string[pos]
                next_node = current_node.get_next_node(char)
                if next_node:
                    current_node = next_node
                    if current_node.is_accepting and current_node.token_ids:
                        selected_token_id = current_node.token_ids[0]
                        last_accepting_node = current_node
                        last_accepting_pos = pos
                    pos += 1
                else:
                    break

            if last_accepting_node is not None and selected_token_id is not None:
                lexeme = input_string[current_position:last_accepting_pos + 1]
                token_name = token_names.get(selected_token_id, "UNKNOWN")

                tokens.append({"TokenName": token_name, "Lexema": lexeme})

                log_entry = f"Token reconocido {
                    repr(lexeme)} con regex {token_name}\n"
                log_file.write(log_entry)

                current_position = last_accepting_pos + 1
            else:
                error_char = input_string[current_position]
                error_msg = f"Error léxico en la posición {
                    current_position}: '{repr(error_char)}'\n"
                log_file.write(error_msg)
                print(error_msg)
                current_position += 1

    return tokens


def process_file(input_data, start_node, token_names, isFile):
    content = ""
    if isFile:
        with open(input_data, 'r') as file:
            while True:
                char = file.read(1)
                if not char:
                    break
                content += char

    else:
        content = input_data

    return lexical_analyzer(content, start_node, token_names)
