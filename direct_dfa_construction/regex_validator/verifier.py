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


# Reading, parsing and storing each regex from a txt file inside a list
def get_formatted_normalized_expressions(file):

    originalExpression, normalizedExp, formattedNormalizedExp = [], [], []
    output_tokens = []

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
                formattedNormalizedExp.append(formatted_normalized_regex)

                output_tokens.append({
                    "nombre": nombre,
                    "regex": formatted_normalized_regex
                })

                # Prints to see if any string may have an error on any of the validation and transformation process
                print(f"\nOriginal Expression: {exp}")
                print(f"Normalized Expression: {normalized_regex}")
                print(f"Formatted Expression: {formatted_normalized_regex}")

                output_file="final_regex_example.json"
                with open(output_file, "w", encoding="utf-8") as outfile:
                    json.dump({"tokens": output_tokens}, outfile, indent=2, ensure_ascii=False)

                print(f"Results saved to {output_file}")
        
    print(f"final format before combining{formattedNormalizedExp}\n ")
    
    return originalExpression, normalizedExp, formattedNormalizedExp, output_tokens