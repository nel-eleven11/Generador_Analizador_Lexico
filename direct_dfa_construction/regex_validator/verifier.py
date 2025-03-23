import json

def simplifyRegex(regex):
    """Simplify redundant expressions in the regex"""
    # Simplify expressions of the form (((expr))) to (expr)
    while True:
        # Find nested parentheses patterns
        i = 0
        simplified = False
        while i < len(regex):
            if regex[i:i+2] == '((':
                # Find the matching closing parentheses
                open_count = 2
                j = i + 2
                while j < len(regex) and open_count > 0:
                    if regex[j] == '(':
                        open_count += 1
                    elif regex[j] == ')':
                        open_count -= 1
                    j += 1
                
                if j < len(regex) and regex[j-2:j] == '))':
                    # Found a pattern like ((expr))
                    inner_expr = regex[i+1:j-1]
                    if isBalanced(inner_expr):
                        # Replace ((expr)) with (expr)
                        regex = regex[:i] + inner_expr + regex[j:]
                        simplified = True
                        break
            i += 1
        
        if not simplified:
            break
    
    # Simplify expressions of the form (expr|ε|ε) to (expr|ε)
    regex = regex.replace('|ε|ε', '|ε')
    
    # Simplify expressions where we have redundant empty string options
    i = 0
    while i < len(regex) - 3:
        if regex[i:i+4] == '()|ε':
            regex = regex[:i] + 'ε' + regex[i+4:]
        i += 1
    
    return regex

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

def isBalanced(expr):
    """Check if an expression has balanced parentheses"""
    stack = []
    for char in expr:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack[-1] != '(':
                return False
            stack.pop()
    return len(stack) == 0

def normalizeRegex(regex):
    """
    Normalize a regular expression by converting ? and + operators to their basic forms
    ? becomes (|ε)
    + becomes a copy followed by *
    """
    # Process the regex character by character
    i = 0
    while i < len(regex):
        # Process question mark operator
        if i + 1 < len(regex) and regex[i + 1] == '?':
            # We have a question mark, figure out what it applies to
            if regex[i] == ')':
                # Find the matching opening parenthesis
                count = 1
                j = i - 1
                while j >= 0 and count > 0:
                    if regex[j] == ')':
                        count += 1
                    elif regex[j] == '(':
                        count -= 1
                    j -= 1
                j += 1
                
                # Extract the group that the ? applies to
                group = regex[j:i+1]
                
                # Remove outer parentheses if group already has form (expr)
                if group.startswith('(') and group.endswith(')'):
                    inner_group = group[1:-1]
                    # Check if inner_group has balanced parentheses
                    if isBalanced(inner_group):
                        # Replace (group)? with (group|ε)
                        regex = regex[:j] + "(" + inner_group + "|ε)" + regex[i+2:]
                    else:
                        # Keep the group as is
                        regex = regex[:j] + "(" + group + "|ε)" + regex[i+2:]
                else:
                    # Replace (group)? with (group|ε)
                    regex = regex[:j] + "(" + group + "|ε)" + regex[i+2:]
                
                # Adjust i to account for the new characters
                i = j + len("(" + inner_group if 'inner_group' in locals() else group + "|ε)")
            else:
                # Single character case: a? becomes (a|ε)
                char = regex[i]
                regex = regex[:i] + "(" + char + "|ε)" + regex[i+2:]
                i += 5  # length of (a|ε)
        
        # Process plus operator
        elif i > 0 and regex[i] == '+':
            if regex[i-1] == ')':
                # Find the matching opening parenthesis
                count = 1
                j = i - 2
                while j >= 0 and count > 0:
                    if regex[j] == ')':
                        count += 1
                    elif regex[j] == '(':
                        count -= 1
                    j -= 1
                j += 1
                
                # Extract the group that the + applies to
                group = regex[j:i]
                
                # Replace (group)+ with (group)(group)*
                regex = regex[:j] + group + group + "*" + regex[i+1:]
                
                # Adjust i to account for the new characters
                i = j + len(group) * 2 + 1  # +1 for *
            else:
                # Single character case: a+ becomes aa*
                char = regex[i-1]
                regex = regex[:i-1] + char + char + "*" + regex[i+1:]
                i += 1  # advance past the *
        else:
            i += 1
    
    # Simplify redundant expressions
    regex = simplifyRegex(regex)
    
    return regex

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
    id_counter = 1

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
                    "regex": formatted_normalized_regex,
                    "id": f"#{id_counter}"
                })

                id_counter += 1

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