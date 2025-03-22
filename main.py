"""
Diseño de Lengujes de Programacion

Autores:
    Nelson García Bravatti
    Joaquín Puente
    Ricardo Chuy

"""

from readYalex import process_yalex_file, simplify_tokens, guardar_tokens_json, transform_let_regex_list

# Definir el archivo yalex a procesar
yalex_file = "yalex_prueba/slr-4.yal"

let_toks, let_re, rule_toks, rule_act = process_yalex_file(yalex_file)
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

