"""
Diseño de Lengujes de Programacion

Autores:
    Nelson García Bravatti
    Joaquín Puente
    Ricardo Chuy

"""

from readYalex import readYalex, process_yalex_file, simplify_tokens

# Definir el archivo yalex a procesar
yalex_file = "slr-4.yal"


# Obtener informacion importante
let_toks, let_re, rule_toks, rule_act = process_yalex_file(yalex_file)
print("Lista de tokens (sección let):")
print(let_toks)
print("\nLista de expresiones regulares (sección let):")
print(let_re)
print("\nLista de tokens (sección rule):")
print(rule_toks)
print("\nLista de acciones o return (sección rule):")
print(rule_act)

# Simplificar y expandir las definiciones para obtener las listas finales
final_tokens, actions = simplify_tokens(let_toks, let_re, rule_toks, rule_act)
print("\nLista de tokens finales (expresiones expandidas):")
print(final_tokens)
print("\nLista de acciones finales:")
print(actions)


