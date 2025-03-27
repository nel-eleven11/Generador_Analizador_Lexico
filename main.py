"""
Diseño de Lengujes de Programacion

Autores:
    Nelson García Bravatti
    Joaquín Puente
    Ricardo Chuy

"""

from pprint import pprint
from readYalex import process_yalex_file, simplify_tokens, guardar_tokens_json, transform_let_regex_list
from lexer import load_dfa, process_file, load_token_names

print("Generador de analizador léxico")

yalex_files = ["yalex_prueba/slr-1.yal", "yalex_prueba/slr-2.yal",
               "yalex_prueba/slr-3.yal", "yalex_prueba/slr-4.yal"]
option = 0

print("Elige un archivo seleccinando el numero correspondiente:")

for index, item in enumerate(yalex_files):
    print(f"{index + 1}. {item}")

option = int(input("\nEleccion: "))

selected_yal = yalex_files[option-1]
print("Opcion seleccionada:", selected_yal)

# Definir el archivo yalex a procesar
# yalex_file = "yalex_prueba/slr-4.yal"

let_toks, let_re, rule_toks, rule_act = process_yalex_file(selected_yal)
print("Lista de tokens (sección let):")
print(let_toks)
print("\nLista de expresiones regulares (sección let):")
print(let_re)
print("\nLista de tokens (sección rule):")
print(rule_toks)
print("\nLista de acciones o return (sección rule):")
print(rule_act)

# Transformar las expresiones de la sección let que usan corchetes
let_re = transform_let_regex_list(let_re)
print("\nLista de expresiones regulares transformadas (sección let):")
print(let_re)

final_tokens, actions = simplify_tokens(let_toks, let_re, rule_toks, rule_act)
print("\nLista de tokens finales (expresiones expandidas):")
print(final_tokens)
print("\nLista de acciones finales:")
print(actions)

# Guardamos en un archivo JSON los tokens finales emparejados con sus acciones
guardar_tokens_json(final_tokens, actions, "expressions.json")
print("\nArchivo 'tokens.json' generado exitosamente.")

# Ejemplo de uso
transitions, acceptance = load_dfa(
    "transition_table.pkl", "acceptance_states.pkl")
token_names = load_token_names('final_out_test.json')
file_path = 'input.txt'  # Ajusta esta ruta según tu archivo

# Procesar el archivo
tokens = process_file(file_path, transitions, acceptance, token_names)

pprint(tokens)
