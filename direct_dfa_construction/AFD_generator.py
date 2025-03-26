from regex_validator.verifier import get_formatted_normalized_expressions
from regex_unifier.unifier import combine_formatted_regex
from ASTNode import AST
import json
import pickle 

def getPrecedence(char):
    precedence = {
        '(': 1,
        '{': 1,
        '[': 1,
        '|': 2,
        '~': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5
    }
    return precedence.get(char, 6)


def infixToPostfix(formattedRegEx):
    openSymbols = ["{", "[", "("]
    closeSymbols = ["}", "]", ")"]

    postfix = ""
    stack = []
    i = 0
    regexLen = len(formattedRegEx)

    while i < regexLen:
        char = formattedRegEx[i]

        # Handle escaped characters
        if char == "\\":
            postfix += char + formattedRegEx[i + 1]  # Add both the escape character and the escaped character
            i += 2
            continue

        elif char.isalnum() or char in 'ε#':
            postfix += char

        elif char in openSymbols:
            stack.append(char)

        elif char in closeSymbols:
            while stack and stack[-1] not in openSymbols:
                postfix += stack.pop()
            if stack:
                stack.pop()  # Pop for the matching opening symbol

        else:
            while stack and stack[-1] != '(' and getPrecedence(stack[-1]) >= getPrecedence(char):
                postfix += stack.pop()
            stack.append(char)

        i += 1

    while stack:
        postfix += stack.pop()

    return postfix

def create_AST_from_combined_postfix():
    expressions, postfixExpressions, formatted_normalized_exp, final_token_list = get_formatted_normalized_expressions("expressions.json")

    #print("my exp", expressions)
    #print(postfixExpressions)
    #print(formatted_normalized_exp)
    print("FInal token list", final_token_list)

    final_regex = combine_formatted_regex(formatted_normalized_exp) 


    # WHen is say normalized i refer to translating an expression like ab? to a(b|ε)
    # That way we only have the core regex simbols |, *, + and concatenation (~)
    print("Exprossions are formatted as follows: OriginalRegex --> NormalizedRegex --> postfixRegex" )

    for idx, exp in enumerate(postfixExpressions):
        if exp != "exit":
            print(f"{idx + 1}. {expressions[idx]}  -->  {formatted_normalized_exp[idx]}  -->  {exp}")
        else:
            print(f"{idx + 1}. {exp}")
        
    print("Result of combining every regex: ", final_regex)

    postfix_final_regex = infixToPostfix(final_regex)

    print("Postfix final regex: ", postfix_final_regex)

    ast = AST(postfix_final_regex)
    ast.draw_ast().render('ast', view=False)

    return ast

def direct_construction_algorithm(ast):
    
    ast.add_position_to_leaves()

    print("\nCalculating nullability")
    ast.calculate_AST_nullability()

    print("\nCalculating first pos")
    ast.calculate_AST_firstPos()

    print("\nCalculating last pos")
    ast.calculate_AST_lastPos()

    print("\nCalculating next pos")
    ast.calculate_AST_nextPos()

    transition_table, acceptance_states = ast.nextPos_table_to_transition_table()

    print("\nTransition table final:\n", transition_table)
    print("\nAcceptance states: ", acceptance_states)

    return transition_table, acceptance_states

def convert_sets_to_lists(obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {key: convert_sets_to_lists(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_sets_to_lists(item) for item in obj]
        else:
            return obj

def save_to_json(dictionary, filename):

    dictionary_converted = convert_sets_to_lists(dictionary)

    with open(filename, 'w') as file:
        json.dump(dictionary_converted, file, indent=4)

def save_to_pickle(dictionary, filename):
    with open(filename, 'wb') as file:
        pickle.dump(dictionary, file)


#ast = get_formatted_normalized_expressions("yal_output_example.json")
ast = create_AST_from_combined_postfix()
transition_table, acceptance_states = direct_construction_algorithm(ast)

#save_to_json(transition_table, "transition_table.json")
#save_to_json(acceptance_states, "acceptance_states.json")

#save_to_pickle(transition_table, "transition_table.pkl")
#save_to_pickle(acceptance_states, "acceptance_states.pkl")