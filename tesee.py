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

def formatRegEx(regex):
    """Format a regular expression by adding concatenation operators (~)"""
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

            # Add concatenation operator where needed
            if (c1 not in openSymbols and c1 not in binaryOperators) and \
               (c2 not in closeSymbols and c2 not in allOperators):
                result += '~'
        else:
            result += c1

        i += 1

    return result

def validateParentheses(regex):
    """Validate that parentheses are correctly balanced in the regex"""
    stack = []
    for i, char in enumerate(regex):
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack:
                return False, f"Unmatched closing symbol at position {i}"
            
            opening = stack.pop()
            if (opening == '(' and char != ')') or \
               (opening == '[' and char != ']') or \
               (opening == '{' and char != '}'):
                return False, f"Mismatched symbols: '{opening}' and '{char}' at position {i}"
    
    if stack:
        return False, f"Unmatched opening symbols: {stack}"
    
    return True, "Parentheses are balanced"

def testNormalization(test_cases):
    """Test the normalization process with the provided test cases"""
    results = []
    
    for regex in test_cases:
        print(f"\nTesting regex: {regex}")
        normalized = normalizeRegex(regex)
        formatted = formatRegEx(normalized)
        valid, message = validateParentheses(normalized)
        
        print(f"Original: {regex}")
        print(f"Normalized: {normalized}")
        print(f"Formatted: {formatted}")
        print(f"Parentheses validation: {message}")
        
        results.append({
            "original": regex,
            "normalized": normalized,
            "formatted": formatted,
            "valid": valid,
            "message": message
        })
    
    return results

# Example usage
test_cases = [
    "(a|b)*abb",
    "ab?",
    "a?b+",
    "(a*|b*)+",
    "0?(1?)?0*",
    "((a|b)+)?"
]

# Run the test
testNormalization(test_cases)