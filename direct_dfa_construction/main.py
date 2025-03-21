import json
from regex_validator.translator import getPostfixExpressionsFromFile
from directAFD import DFA
from ASTNode import AST
import copy

expressions, postfixExpressions, normalizedExpressions = getPostfixExpressionsFromFile("yal_output_example.json")

print("my exp", expressions)
print(postfixExpressions)
print(normalizedExpressions)

postfixExpressions.append("exit")


option = -1
expressionsCount = len(postfixExpressions)

while option != expressionsCount:

    print("\nWelcome, which expression do you want to test?")

    # WHen is say normalized i refer to translating an expression like ab? to a(b|ε)
    # That way we only have the core regex simbols |, *, + and concatenation (~)
    print("Exprossions are formatted as follows: OriginalRegex --> NormalizedRegex --> postfixRegex" )

    for idx, exp in enumerate(postfixExpressions):
        if exp != "exit":
            print(f"{idx + 1}. {expressions[idx]}  -->  {normalizedExpressions[idx]}  -->  {exp}")
        else:
            print(f"{idx + 1}. {exp}")
            
    option = int(input())

    postfix_list_len = len(postfixExpressions)

    if postfixExpressions == option or option > postfix_list_len:
        break

    selected_postfix_expression = postfixExpressions[option - 1]
    selectedRegex = expressions[option -1]
    selectedNormalReg = normalizedExpressions[option -1]

    ast = AST(selected_postfix_expression)

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

    ast.draw_ast().render('ast', view=False)

    dfa = DFA(transition_table, acceptance_states, ast.alphabet)
    dfa.draw_dfa('dfa')
    min_dfa = copy.deepcopy(dfa) 
    mdfa = min_dfa.minimize()
    mdfa.draw_dfa('min_dfa')
    test_string = input("Enter a string to test: ")
    if dfa.verifyString(test_string):
        print("Accepted!")
    else:
        print("Rejected!")
