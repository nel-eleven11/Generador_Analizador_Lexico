# Diseño de Lenaguajes de Programación
"""
Autores:
    Nelson García Bravatti
    Joaquín Puente
    Ricardo Chuy
Archivo:
    Este archivo se encarga de leer los archivos YALex para luego crear un archivo json con las expresiones regulares.

"""

import json

special_chars = set("+*()[]{}?~")

class readYalex:
    def __init__(self, yalex_file):
        self.yalex_file = yalex_file
        self.tamanio_buffer = 10
        self.inicio = 0
        self.avance = 10

    def read_file(self):
        with open(self.yalex_file, "r", encoding="utf-8") as f:
            return list(f.read())

# Funciones auxiliares para extraer tokens (palabras o grupos) del archivo

def unescape_string(s):
    return s.encode('utf-8').decode('unicode_escape')

# Función auxiliar para procesar caracteres especiales
def process_special_chars(s):
    new_s = ""
    for ch in s:
        if ch in special_chars:
            new_s += "\\" + ch  # Agrega dos barras invertidas antes del carácter
        else:
            new_s += ch
    return new_s 

def read_group(entrada, index, open_char, close_char):
    """
    Lee desde 'open_char' hasta encontrar el 'close_char'
    y luego sigue concatenando hasta encontrar un espacio.
    """
    token = ""
    count_com = 0
    # Agrega el caracter de apertura
    token += entrada[index]
    index += 1
    # Lee hasta encontrar el caracter de cierre
    while (index < len(entrada)) and (entrada[index] != close_char) and (count_com % 2 == 0) :
        if entrada[index] in ["'", '"']:
            count_com += 1
        if (entrada[index] in special_chars) and (count_com % 2 == 1):
            #print("char escp gp")
            token += process_special_chars(entrada[index])
        else:
            token += entrada[index]
        index += 1
    # Agrega el caracter de cierre (si existe)
    if index < len(entrada):
        token += entrada[index]
        index += 1
    # Luego, sigue concatenando caracteres hasta topar con un espacio en blanco
    while index < len(entrada) and not entrada[index].isspace():
        if entrada[index] in ["'", '"']:
            count_com += 1
        if (entrada[index] in special_chars) and (count_com % 2 == 1):
            #print("char escp gp pas")
            token += process_special_chars(entrada[index])
        else:
            token += entrada[index]
        index += 1
    return token, index

def read_quoted(entrada, index):
    """
    Lee una secuencia iniciada por comillas simples o dobles,
    concatenando hasta encontrar la comilla de cierre y continuando
    hasta el siguiente espacio en blanco.
    """
    quote_char = entrada[index]
    token = ""
    #token += quote_char
    index += 1
    while index < len(entrada) and entrada[index] != quote_char:
        if entrada[index] in special_chars:
            token += process_special_chars(entrada[index])
        else:
            token += entrada[index]
        index += 1
    if index < len(entrada):
        #token += entrada[index]
        index += 1
    while index < len(entrada) and not entrada[index].isspace():
        token += entrada[index]
        index += 1
    return token, index

def read_token(entrada, index):
    """
    Lee y retorna un token desde la posición 'index' hasta encontrar un espacio en blanco.
    Si encuentra caracteres especiales (grupos entre [] o () o comillas) los procesa en conjunto.
    """
    token = ""
    while index < len(entrada) and not entrada[index].isspace():
        char = entrada[index]
        if char in ["[", "("]:
            # Para corchetes o paréntesis se lee hasta su cierre correspondiente
            close_char = "]" if char == "[" else ")"
            token_part, index = read_group(entrada, index, char, close_char)
            token += token_part
        elif char in ["'", '"']:
            # Para comillas simples o dobles
            token_part, index = read_quoted(entrada, index)
            token += token_part
        else:
            token += char
            index += 1
    return token, index

def process_yalex_file(filename):
    """
    Procesa el archivo YALex para extraer:
      - let_tokens: nombres de tokens de la sección 'let'
      - let_regex: expresiones regulares correspondientes
      - rule_tokens: tokens (o regex) de la sección 'rule'
      - rule_actions: acción de retorno asociada (cadena vacía si no hay acción)
    """
    # Leemos el archivo completo como lista de caracteres
    ry = readYalex(filename)
    entrada = ry.read_file()
    index = 0
    tokens = []
    # Se recorre la entrada carácter a carácter, extrayendo tokens
    while index < len(entrada):
        # Se salta cualquier espacio en blanco
        if entrada[index].isspace():
            index += 1
            continue
        tk, index = read_token(entrada, index)
        tokens.append(tk)
    
    # Ahora procesamos la lista de tokens para llenar nuestras 4 listas
    let_tokens = []
    let_regex = []
    rule_tokens = []
    rule_actions = []
    
    section = None  # Indica la sección actual: None, "let" o "rule"
    i = 0
    while i < len(tokens):
        token = tokens[i]
        # Si se encuentra la palabra "rule" se cambia a la segunda sección
        if token.lower() == "rule":
            section = "rule"
            i += 1
            continue
        
        # Procesamiento de la sección let (definición de tokens y regex)
        if section != "rule":
            if token.lower() == "let":
                # Se espera el formato: let <nombre> = <expresión>
                if i + 3 < len(tokens) and tokens[i+2] == "=":
                    nombre = tokens[i+1]
                    # Aplicamos un unescape a la expresión regular
                    regex_exp = unescape_string(tokens[i+3])
                    let_tokens.append(nombre)
                    let_regex.append(regex_exp)
                    i += 4
                    continue
            i += 1
        else:
            # En la sección rule se ignoran tokens como "=" o "tokens" (del encabezado)
            if token.lower() == "tokens":
                i += 2  
                continue
            # Omitir comentarios (* *)
            if "(*" in token:
                i += 1
                continue
            # El carácter '|' indica separación entre reglas
            if token == "|":
                i += 1
                continue
            # Se asume que el token actual es el patrón de la regla
            patron = token
            accion = ""
            i += 1
            # Si el siguiente token es "{" se procesa la acción
            if i < len(tokens) and tokens[i] == "{":
                i += 1  # Se salta "{"
                if i < len(tokens) and tokens[i].lower() == "return":
                    i += 1  # Se salta "return"
                    if i < len(tokens):
                        accion = tokens[i]
                        i += 1
                # Se salta hasta encontrar "}"
                while i < len(tokens) and tokens[i] != "}":
                    i += 1
                if i < len(tokens) and tokens[i] == "}":
                    i += 1
            else:
                accion = token
                i += 1
            rule_tokens.append(patron)
            rule_actions.append(accion)
    
    return let_tokens, let_regex, rule_tokens, rule_actions


def custom_replace(expr, key, replacement):
    """
    Reemplaza todas las ocurrencias de 'key' en 'expr' por 'replacement'
    respetando límites de palabra (se verifica que el carácter anterior y posterior
    no sean alfanuméricos).
    """
    result = ""
    i = 0
    key_len = len(key)
    while i < len(expr):
        # Verificar si en la posición i se encuentra 'key'
        if expr[i:i+key_len] == key:
            left_boundary = (i == 0) or (not expr[i-1].isalnum())
            right_index = i + key_len
            right_boundary = (right_index >= len(expr)) or (not expr[right_index].isalnum())
            if left_boundary and right_boundary:
                result += replacement
                i += key_len
                continue
        result += expr[i]
        i += 1
    return result

def expand_expression(expression, definitions):
    """
    Expande recursivamente en 'expression' las referencias a tokens definidos en 'definitions'.
    Se reemplazan ocurrencias que coincidan con límites de palabra.
    """
    previous = None
    new_expr = expression
    # Ordenar las claves por longitud decreciente para evitar conflictos
    sorted_keys = sorted(definitions.keys(), key=lambda k: len(k), reverse=True)
    while new_expr != previous:
        previous = new_expr
        for key in sorted_keys:
            new_expr = custom_replace(new_expr, key, definitions[key])
    return new_expr

def simplify_tokens(let_tokens, let_regex, rule_tokens, rule_actions):
    """
    Simplifica los tokens de la sección rule usando las definiciones de la sección let.
    Retorna dos listas:
      - final_tokens: tokens en su forma expandida (por ejemplo, "ws" se transforma en "[' ''\t''\n']+")
      - actions: las acciones o returns asociados (idénticas a rule_actions)
    """
    # Construir el diccionario de definiciones
    definitions = {}
    for name, regex in zip(let_tokens, let_regex):
        definitions[name] = regex

    final_tokens = []
    for token in rule_tokens:
        if token in definitions:
            expanded = expand_expression(definitions[token], definitions)
            final_tokens.append(expanded)
        else:
            final_tokens.append(token)
    actions = rule_actions[:]  # Copia de la lista
    return final_tokens, actions


def guardar_tokens_json(final_tokens, actions, output_file):
    """
    Crea un archivo JSON con la siguiente estructura:
    {
        "tokens": [
            {
                "nombre": <acción o return>,
                "regex": <token expandido>
            },
            ...
        ]
    }
    Los elementos se crean emparejando cada token final con su acción correspondiente.
    """
    tokens_list = []
    for nombre, regex in zip(actions, final_tokens):
        tokens_list.append({
            "nombre": nombre,
            "regex": regex
        })
    data = {"tokens": tokens_list}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def parse_bracket(expr, i):
    """
    Dado que en expr[i] se encuentra un '[', se procesa el grupo hasta el correspondiente ']'
    y se transforma en una agrupación con alternancia.
    Se extraen los tokens (entre comillas) y se detectan rangos (p.ej., '0'-'9').
    Soporta grupos anidados.
    
    Retorna una tupla (transformed, nuevo_indice)
    """
    alternatives = []
    i += 1  # saltar '['
    while i < len(expr) and expr[i] != ']':
        if expr[i].isspace():
            i += 1
            continue
        # Procesar token entre comillas
        if expr[i] in ["'", '"']:
            quote = expr[i]
            i += 1
            token_val = ""
            while i < len(expr) and expr[i] != quote:
                token_val += expr[i]
                i += 1
            i += 1  # saltar comilla de cierre
            # Si es doble comilla, se toman cada uno de sus caracteres por separado
            if quote == '"':
                for ch in token_val:
                    alternatives.append(ch)
            else:
                alternatives.append(token_val)
            # Verificar si se define un rango (por ejemplo, '0'-'9')
            if i < len(expr) and expr[i] == '-':
                i += 1  # saltar '-'
                if i < len(expr) and expr[i] in ["'", '"']:
                    quote2 = expr[i]
                    i += 1
                    token_val2 = ""
                    while i < len(expr) and expr[i] != quote2:
                        token_val2 += expr[i]
                        i += 1
                    i += 1  # saltar comilla de cierre
                    if len(token_val) == 1 and len(token_val2) == 1:
                        # Se elimina el token anterior y se expande el rango
                        alternatives.pop()
                        for c in range(ord(token_val), ord(token_val2) + 1):
                            alternatives.append(chr(c))
                    # Si no son de un solo carácter, se puede definir otro comportamiento
                else:
                    alternatives.append('-')
        elif expr[i] == '[':
            # Grupo anidado: se procesa recursivamente.
            nested_trans, i = parse_bracket(expr, i)
            alternatives.append(nested_trans)
        else:
            # Cualquier otro carácter se agrega tal cual.
            alternatives.append(expr[i])
            i += 1
    if i < len(expr) and expr[i] == ']':
        i += 1  # saltar ']'
    transformed = "(" + "|".join(alternatives) + ")"
    return transformed, i


def transform_brackets(expr):
    """
    Procesa la expresión expr y reemplaza cada grupo entre corchetes [ ... ]
    por una agrupación con alternancia, aplicando recursividad para grupos anidados.
    """
    result = ""
    i = 0
    while i < len(expr):
        if (expr[i] == '[') and (expr[i-1] != '\\'):
            trans, i = parse_bracket(expr, i)
            result += trans
        else:
            result += expr[i]
            i += 1
    return result

def remove_useless_quotes(expr):
    """
    Recorre la expresión expr y elimina las comillas simples o dobles que encierran
    un contenido sin propósito, es decir, convierte 'a' o "a" en a.
    """
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] in ["'", '"']:
            quote = expr[i]
            i += 1
            temp = ""
            while i < len(expr) and expr[i] != quote:
                temp += expr[i]
                i += 1
            if i < len(expr) and expr[i] == quote:
                i += 1  # saltar comilla de cierre
            result += temp
        else:
            result += expr[i]
            i += 1
    return result


def transform_let_regex_list(let_regex):
    """
    Recorre la lista let_regex y, para cada expresión que contenga corchetes, aplica
    la transformación para generar una expresión más "plana" basada en la alternancia.
    Además, antes de procesar se verifica si la expresión contiene un espacio en blanco
    delimitado por comillas (' ' o " ") y se reemplaza por el caracter épsilon ε.
    Luego se elimina cualquier comilla innecesaria.
    """
    new_let_regex = []
    for regex in let_regex:
        # Reemplazar espacios en blanco entre comillas por ε
        regex = regex.replace("' '", "'  '").replace('" "', "'  '")
        if '[' in regex:
            new_regex = transform_brackets(regex)
        else:
            new_regex = regex
        new_regex = remove_useless_quotes(new_regex)
        new_let_regex.append(new_regex)
    return new_let_regex

