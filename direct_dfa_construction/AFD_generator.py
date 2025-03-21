from regex_validator.verifier import get_formatted_normalized_expressions
from regex_unifier.unifier import combine_formatted_regex
from ASTNode import AST
from directAFD import DFA
import copy

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
    keywords = ["if", "else", "com", "net", "org"]

    postfix = ""
    stack = []
    i = 0
    regexLen = len(formattedRegEx)

    while i < regexLen:
        char = formattedRegEx[i]

        # Handle keywords like 'if' and 'else'
        if char.isalpha():
            keyword = ""
            while i < regexLen and formattedRegEx[i].isalpha():
                keyword += formattedRegEx[i]
                i += 1
            if keyword in keywords:
                postfix += keyword
                continue
            else:
                postfix += keyword
                char = ''
                i -= 1

        # Handle escaped characters
        elif char == "\\":
            postfix += formattedRegEx[i + 1]
            i += 2
            continue

        elif char.isalnum() or char in 'ε':
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
    expressions, postfixExpressions, formatted_normalized_exp, final_token_list = get_formatted_normalized_expressions("yal_output_example.json")

    #print("my exp", expressions)
    #print(postfixExpressions)
    #print(formatted_normalized_exp)
    print("FInal token list", final_token_list)

    final_regex = combine_formatted_regex(formatted_normalized_exp) 

    print("\nWelcome, which expression do you want to test?")

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

create_AST_from_combined_postfix()
# ast.add_position_to_leaves()

# print("\nCalculating nullability")
# ast.calculate_AST_nullability()

# print("\nCalculating first pos")
# ast.calculate_AST_firstPos()

# print("\nCalculating last pos")
# ast.calculate_AST_lastPos()

# print("\nCalculating next pos")
# ast.calculate_AST_nextPos()

# transition_table, acceptance_states = ast.nextPos_table_to_transition_table()

# print("\nTransition table final:\n", transition_table)
# print("\nAcceptance states: ", acceptance_states)



# dfa = DFA(transition_table, acceptance_states, ast.alphabet)
# dfa.draw_dfa('dfa')
# min_dfa = copy.deepcopy(dfa) 
# mdfa = min_dfa.minimize()
# mdfa.draw_dfa('min_dfa')
# test_string = input("Enter a string to test: ")
# if dfa.verifyString(test_string):
#     print("Accepted!")
# else:
#     print("Rejected!")
