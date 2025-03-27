import pickle

import json


def load_token_names(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    token_names = {token['id']: token['nombre'] for token in data['tokens']}
    return token_names


def load_dfa(transitions_file, acceptance_file):
    with open(transitions_file, 'rb') as f:
        transitions = pickle.load(f)
    with open(acceptance_file, 'rb') as f:
        acceptance = pickle.load(f)
    return transitions, acceptance


def lexical_analyzer(input_string, transitions, acceptance, token_names):
    tokens = []
    current_position = 0

    while current_position < len(input_string):
        state = 0 
        pos = current_position
        last_accepting_state = None
        last_accepting_pos = None
        selected_token_id = None

        while pos < len(input_string):
            char = input_string[pos]
            if (state in transitions and
                'transitions' in transitions[state] and
                    char in transitions[state]['transitions']):
                state = transitions[state]['transitions'][char]
                if state in acceptance:
                    ids = acceptance[state]
                    if ids:
                        selected_token_id = ids[0]
                        last_accepting_state = state
                        last_accepting_pos = pos
                pos += 1
            else:
                break

        if last_accepting_state is not None and selected_token_id is not None:
            lexeme = input_string[current_position: last_accepting_pos + 1]
            token_name = token_names.get(selected_token_id, "UNKNOWN")


            tokens.append({"TokenName": token_name, "Lexema": lexeme})
            current_position = last_accepting_pos + 1
        else:
            error_char = input_string[current_position]
            print(f"Error léxico en la posición {
                  current_position}: '{error_char}'")
            break

    return tokens


def process_file(file_path, transitions, acceptance, token_names):

    all_tokens = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            print(f"Procesando línea {line_number}: {line}")
            tokens = lexical_analyzer(
                line, transitions, acceptance, token_names)
            all_tokens.extend(tokens)

            for token in tokens:
                print(f"  Token: {token['TokenName']
                                  }, Lexema: {token['Lexema']}")

    return all_tokens
