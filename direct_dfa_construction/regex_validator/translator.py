import json

def stackTopMatchesSimbol(char, stack):
    if char == ")" and stack[-1] == "(":
        return True
    elif char == "]" and stack[-1] == "[":
        return True
    elif char == "}" and stack[-1] == "{":
        return True
    return False

# Method to determine if a expression is balanced
def expressionIsBalanced(regex):
    stack = []
    charList = list(regex)
    
    openSimbols = ["{", "[", "("]
    closeSimbols = ["}", "]", ")"]
    
    # Iterating on each character of a regex
    for char in charList:
        # Checking if the symbol is an open bracket
        if char in openSimbols:
            stack.append(char)
            print(f"Added {char} to stack: {stack}")
        # And here if its a closed bracket
        elif char in closeSimbols:
            # If stack is empty (no corresponding opening bracket is found) 
            if len(stack) == 0:
                print(f"Found {char} but stack is empty: {stack}")
                return False
            # If it is not empty and also the top of the stack is a matching opening bracket for the current closing bracket
            elif stackTopMatchesSimbol(char, stack):
                popped = stack.pop()
                print(f"Matching {char} with {popped}, stack after pop: {stack}")
            # If the top of the stack does not match the closing bracket
            elif not stackTopMatchesSimbol(char, stack):
                print(f"Found {char} but top of stack {stack[-1]} does not match: {stack}")
                return False
    
    if len(stack) == 0:
        print(f"Stack is empty after processing all characters: {stack}")
        return True
    else:
        print(f"Stack is not empty after processing all characters: {stack}")
        return False

def normalizePlusSign(regex):
    normalized = ""
    stack = []
    i = 0
    while i < len(regex):
        if regex[i] == '+' and i > 0:
            subexpr = ""
            if regex[i - 1] in [')', ']']:
                # Find the matching opening symbol
                open_symbols = {'(': ')', '[': ']'}
                close_symbols = {')': '(', ']': '['}
                open_symbol = close_symbols[regex[i - 1]]
                open_parens = 1
                j = i - 2
                while j >= 0 and open_parens > 0:
                    if regex[j] == open_symbol:
                        open_parens -= 1
                    elif regex[j] == regex[i - 1]:
                        open_parens += 1
                    j -= 1
                j += 1
                subexpr = regex[j:i]
                normalized = normalized[:j] + f"{subexpr}{subexpr}*"
            else:
                subexpr = regex[i - 1]
                normalized = normalized[:-1] + f"{subexpr}{subexpr}*"
        else:
            normalized += regex[i]
        i += 1
    return normalized

def normalizeRegex(regex):
    # Normalize the `?` first
    

    if "?" in regex:

        normalized = ""
        i = 0
        while i < len(regex):
            if i + 1 < len(regex) and regex[i + 1] == '?':
                if regex[i] == ")":
                    normalized += f"|ε)"
                else:
                    normalized += f"({regex[i]}|ε)"
                i += 2
            else:
                normalized += regex[i]
                i += 1
        # Then normalize the `+`
        normalized = normalizePlusSign(normalized)
        return normalized
    else:
        normalized = normalizePlusSign(regex)
        return normalized

    

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

def formatRegEx(regex):
    allOperators = ['|', '?', '+', '*', '^']
    binaryOperators = ['^', '|']
    openSymbols = ["{", "[", "("]
    closeSymbols = ["}", "]", ")"]

    regexLen = len(regex)
    result = ""
    i = 0

    while i < regexLen:
        c1 = regex[i]

        if i + 1 < regexLen:
            c2 = regex[i + 1]

            result += c1

            # Check for escaped characters
            if c1 == "\\":
                result += c2
                i += 2
                continue

            if c1 not in openSymbols and c2 not in closeSymbols and c2 not in allOperators and c1 not in binaryOperators:
                result += '~'
        else:
            result += c1

        i += 1

    return result

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

# Reading, parsing and storing each regex from a txt file inside a list
def getPostfixExpressionsFromFile(file):

    originalExpression, normalizedExp, postfixExpressions = [], [], []

    with open(file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    tokens = json_data.get('tokens', [])

    for token in tokens:
        nombre = token.get('nombre')
        regex = token.get('regex')
        exp = regex.replace(" ", "")

        if expressionIsBalanced(exp):
                #its necesarry to concatenate the # at the end firs before starting to process the regex
                originalExpression.append(exp)

                # Normalize means changing the + and ? operators
                normalized_regex = normalizeRegex(exp+"#") 
                normalizedExp.append(normalized_regex)

                #formatting means adding the concatenation "~" symbol
                formatted_normalized_regex = formatRegEx(normalized_regex)

                #infix to postfix of formatted string
                postfix_formatted_normalized_regex = infixToPostfix(formatted_normalized_regex)
                postfixExpressions.append(postfix_formatted_normalized_regex)

                # Prints to see if any string may have an error on any of the validation and transformation process
                print(f"\nOriginal Expression: {exp}")
                print(f"Normalized Expression: {normalized_regex}")
                print(f"Formatted Expression: {formatted_normalized_regex}")
                print(f"infix Expression: {postfix_formatted_normalized_regex}")

    print("Infix a Postfix: \n")
    
    return originalExpression, postfixExpressions, normalizedExp