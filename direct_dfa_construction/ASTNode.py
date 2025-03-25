from graphviz import Digraph

class ASTNode:
    def __init__(self, value: str, left=None, right=None):
        self.value = value
        self.left: ASTNode = left
        self.right: ASTNode = right
        self.isNullable = False
        self.position = 0
        self.firstPos = set()
        self.lastPos = set()
        self.nextPos = set()
        

class AST:
    def __init__(self, postfix_expression: str):
        self.regex_counter = 0
        self.hashtag_id_list = []
        self.root: ASTNode = self.postfixToAst(postfix_expression)
        self.nextPosTable = {}
        self.alphabet = set()
        self.end_state = {}

    def postfixToAst(self, postfix):
        #reserved simbols, that will help later in some validations
        
        operators_and_reserved = {'|', '~', '*', '#', 'ε'}

        stack = []
        i = 0
        postfix_len = len(postfix)

        while i < postfix_len:
            char = postfix[i]

            # Handle escaped characters
            if char == "\\":
                # Combine the escape character and the next character
                escaped_char = char + postfix[i + 1]
                node = ASTNode(escaped_char)
                stack.append(node)
                print(f"Found escaped character {escaped_char}, pushing to the stack")
                i += 2  # Skip the next character
                continue

            # Handle alphanumeric characters, epsilon, and special characters
            elif char.isalnum() or char == "ε" or char not in operators_and_reserved:
                node = ASTNode(char)
                stack.append(node)
                print(f"Found {char}, pushing symbol to the stack")

            elif char == "#":
                # Asignar un identificador único al #
                self.regex_counter += 1
                unique_id = f"#{self.regex_counter}"
                self.hashtag_id_list.append(unique_id)
                node = ASTNode(unique_id)
                stack.append(node)
                print(f"Found {char}, assigning unique ID {unique_id}, and pushing to the stack")

            elif char in {'|', '~'}:
                # Binary operators: pop two operands from the stack
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands for binary operator {char}")
                right = stack.pop()
                left = stack.pop()
                node = ASTNode(char, left, right)
                stack.append(node)
                print(f"Found binary operator {char}, retrieving {right.value} and {left.value}, assigning them to the right and left children respectively, and pushing {char} to the stack")

            elif char == "*":
                # Unary operator: pop one operand from the stack
                if len(stack) < 1:
                    raise ValueError(f"Not enough operands for unary operator {char}")
                left = stack.pop()
                node = ASTNode(char, left)
                stack.append(node)
                print(f"Found {char}, retrieving {left.value} and assigning it as left child, then pushing {char} to the stack")

            else:
                raise ValueError(f"Unknown character in postfix expression: {char}")

            i += 1

        print("Unique hashtag ID's:", self.hashtag_id_list)

        if len(stack) != 1:
            raise ValueError("Invalid postfix expression: stack does not contain exactly one element")

        return stack.pop()

    def draw_ast(self):
        dot = Digraph()
        
        def add_nodes_edges(node):
            if node.left:
                dot.node(str(id(node.left)), node.left.value)
                dot.edge(str(id(node)), str(id(node.left)))
                add_nodes_edges(node.left)
            if node.right:
                dot.node(str(id(node.right)), node.right.value)
                dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.right)
        
        if self.root:
            dot.node(str(id(self.root)), self.root.value)
            add_nodes_edges(self.root)
            
        return dot
    
    def add_position_to_leaves(self):

        def position_for_node(root: ASTNode, pos_counter) -> None:

            # If node is null, return
            if (not root):
                return

            # If node is leaf node, 
            # print its data
            if (not root.left and not root.right):

                root.position = pos_counter[0]

                # now we changed so the root value is not in the ID's #1, #2 ..., # is not part of the alphabet
                if root.value not in ["ε", "*", "|", "~"] and root.value not in self.hashtag_id_list:
                    self.alphabet.update([root.value])

                # Tis will initialize the table for next pos. So later we dont have to traverse the tree again.
                if root.value != "ε":
                    
                    self.nextPosTable[pos_counter[0]] = {'value': root.value, 'nextPos': set()}
                    pos_counter[0] += 1

                    # also here we adentify the number of the node that has #
                    if root.value in self.hashtag_id_list:
                        self.end_state[root.value] = root.position  # Usamos un diccionario para mapear #_i a su posición
                    
                    print(f"{root.value},{root.position}", end = " ")

                return

            # If left child exists, 
            # check for leaf recursively
            if root.left:
                position_for_node(root.left, pos_counter)
                

            # If right child exists, 
            # check for leaf recursively
            if root.right:
                position_for_node(root.right, pos_counter)
            
        position_counter = [1]
        position_for_node(self.root, position_counter)
        print("\n\nTable for next pos: \n",self.nextPosTable)
        print("\nAlphabet: ", self.alphabet)
        print("\nNumber of the state with '#': ", self.end_state)

    
    def calculate_AST_nullability(self):

        if self.root is None:
            return
        
        def nullable(node: ASTNode):
            
            if node is None:
                return False
            
            # Post order
            left_nullable = nullable(node.left)
            right_nullable = nullable(node.right)
        
            if node.value == "ε":
                node.isNullable = True
                print(f"The node with value: {node.value} nullability is {True}")
                return True
            
            # all nodes that are not a leaf have position 0.
            elif node.position > 0:
                node.isNullable = False 
                print(f"The node with value: {node.value} nullability is {False}")
                return False

            elif node.value == "|":
                # if any of the child nodes is nullable, so is the node that has the | oeprator
                node.isNullable = left_nullable or right_nullable
                print(f"The node with value: {node.value} nullability is {node.isNullable}")
                return node.isNullable
                
            
            elif node.value == "~":
                # if bothe of the childe nodes are nullable, the node with ~ is also nullable
                node.isNullable = left_nullable and right_nullable
                print(f"The node with value: {node.value} nullability is {node.isNullable}")
                return node.isNullable

            elif node.value == "*":
                node.isNullable = True
                print(f"The node with value: {node.value} nullability is {True}")
                return True

        nullable(self.root)
    
    def calculate_AST_firstPos(self):

        if self.root is None:
            return
        
        def first_pos(node: ASTNode):
            
            if node is None:
                return set()
            
            # Post order
            left_firstPos: set = first_pos(node.left)
            right_firstPos: set = first_pos(node.right)
        
            if node.value == "ε":
                node.firstPos = set()
                print(f"The node with value: {node.value} has first pos:{ node.firstPos }")
                return node.firstPos
                
            # all nodes that are not a leaf have position 0.
            elif node.position > 0:
                node.firstPos = set([node.position]) 
                print(f"The node with value: {node.value} has first pos:{ node.firstPos }")
                return node.firstPos

            elif node.value == "|":
                node.firstPos = left_firstPos.union(right_firstPos)

                print(f"The node with value: {node.value} has first pos:{ node.firstPos }")
                return node.firstPos
            
            elif node.value == "~":

                if(node.left.isNullable):
                    node.firstPos = left_firstPos.union(right_firstPos)
                    print(f"The node with value: {node.value} has first pos:{ node.firstPos }")
                    return node.firstPos
                else:
                    node.firstPos = left_firstPos
                    print(f"The node with value: {node.value} has first pos:{ node.firstPos }")
                    return node.firstPos

            elif node.value == "*":
                node.firstPos = left_firstPos
                print(f"The node with value: {node.value} has first pos:{ node.firstPos }")
                return node.firstPos
            
        first_pos(self.root)

    def calculate_AST_lastPos(self):

        if self.root is None:
            return
        
        def last_pos(node: ASTNode):
            
            if node is None:
                return set()
            
            # Post order
            left_lastPos: set = last_pos(node.left)
            right_lastPos: set = last_pos(node.right)
        
            if node.value == "ε":
                node.lastPos = set()
                print(f"The node with value: {node.value} has last pos:{ node.lastPos }")
                return node.lastPos
                
            # all nodes that are not a leaf have position 0.
            elif node.position > 0:
                node.lastPos = set([node.position]) 
                print(f"The node with value: {node.value} has last pos:{ node.lastPos }")
                return node.lastPos

            elif node.value == "|":
                node.lastPos = left_lastPos.union(right_lastPos)

                print(f"The node with value: {node.value} has last pos:{ node.lastPos }")
                return node.lastPos
            
            elif node.value == "~":

                if(node.right.isNullable):
                    node.lastPos = left_lastPos.union(right_lastPos)
                    print(f"The node with value: {node.value} has last pos:{ node.lastPos }")
                    return node.lastPos
                else:
                    node.lastPos = right_lastPos
                    print(f"The node with value: {node.value} has last pos:{ node.lastPos }")
                    return node.lastPos

            elif node.value == "*":
                node.lastPos = left_lastPos
                print(f"The node with value: {node.value} has last pos:{ node.lastPos }")
                return node.lastPos
            
        last_pos(self.root)

    def calculate_AST_nextPos(self):

        if self.root is None:
            return
        
        def next_pos(node: ASTNode):
            
            if node is None:
                return

            # post order traversal will be used now.
            next_pos(node.left)
            next_pos(node.right)
            
            if node.value == "~":

                left_lastPos = node.left.lastPos
                print(f"\nFound ~ node with left child lastpos: {left_lastPos}")

                for position in left_lastPos:
                    right_firstPos = node.right.firstPos
                    print(f"For position {position}, adding set from right child first pos: {right_firstPos}")
                    self.nextPosTable[position]["nextPos"].update(right_firstPos) 

            elif node.value == "*":
                
                node_lastPos = node.lastPos
                print(f"\nFound * node with lastpos: {node.lastPos}")

                for position in node_lastPos:
                    left_firstPos = node.left.firstPos
                    print(f"For position {position}, adding set of left child first pos: {left_firstPos}")
                    self.nextPosTable[position]["nextPos"].update(left_firstPos) 
                    
        next_pos(self.root)
        print("Resulting Next Position table:\n", self.nextPosTable)
    
    def getAlias(sef,transitionTable, positions_compare):
        for index in transitionTable:
            item = transitionTable[index]
            if item["positions"] == positions_compare:
                return index
        
        return ""
    
    def clean_transition_symbol(self, symbol):
        # Diccionario de caracteres especiales que deben conservarse
        special_chars = {
            't': '\t',
            'n': '\n',
            'r': '\r',
            '\\': '\\'  
        }
        
        # escaped chars
        if len(symbol) > 1 and symbol[0] == '\\':
            char = symbol[1]
           
            if char in special_chars:
                return special_chars[char]
            
            return char
       
        return symbol
    
        
    def clean_transition_table(self, transition_table):
        cleaned_table = {}
        for state, data in transition_table.items():
            cleaned_transitions = {}
            for symbol, target in data['transitions'].items():
                cleaned_symbol = self.clean_transition_symbol(symbol)
                cleaned_transitions[cleaned_symbol] = target
            cleaned_table[state] = {
                'positions': data['positions'],
                'transitions': cleaned_transitions
            }
        return cleaned_table
        
    def nextPos_table_to_transition_table(self):
        # the table format is like this { 1: {'value': 'a', 'nextPos': {1,2,3}, ... }
        # this means that leaf 1 has a value of a and a nextPos set of {1,2,3}
        np_table = self.nextPosTable
        np_table = self.nextPosTable
        state_counter = 0
        next_node_counter = 1

        # the ransition wil be a dictionary of dictionaries
        # the first key will be the number of the node and the value will be its transitions
        # so { 0: {positions:{1,2,3} transitions: {a: 2, b: 1} } } means state 0, has the positions {1,2,3} from the ast
        # and taht with "a" moves to state 2, and with "b" moves to state 1 (POSITIONS and states are not the same)
        transition_table = {}
        
        # turning sets to frozensts for consistency
        all_sets = set([frozenset(sorted(self.root.firstPos))])
        evaluated_sets = set()

        # order alfabet
        alphabet = sorted(list(self.alphabet))

        transition_table[state_counter] = {"positions": set(self.root.firstPos), "transitions": {}}

        while all_sets - evaluated_sets:
            # using always the first set not evaluated
            selected_set = next(iter(all_sets - evaluated_sets))

            # for each letter in the alphabet
            for char in alphabet:
                union_sigPos = set()

                print(f"Currently testing set {set(selected_set)}, with alphabet: {char}")

                # Here is the point when a node does not have a transition with letter of the alphabet.
                # dead states can be implemented here also, but for simplicity of the DFA drawing we are skiping if the 
                # node does not have transitions with a specific alphabet letter
                for position in selected_set:
                    if np_table[position]["value"] == char:
                        union_sigPos.update(np_table[position]["nextPos"])

                if not union_sigPos:
                    continue 

                 # now we have to check if said set already exists 
                found_alias = None
                for idx, state in transition_table.items():
                    if state["positions"] == union_sigPos:
                        found_alias = idx
                        break

                if found_alias is None:
                    # new state
                    print(f"There is no set with the union positions {set(union_sigPos)}, ({state_counter},{char}) -> {union_sigPos} so we asign = {next_node_counter}")
                    #add transition to the tstae we are evaluating (1,a) -> 2, on state 1 with a we move to 2 for example
                    transition_table[next_node_counter] = {
                        "positions": union_sigPos, 
                        "transitions": {}
                    }
                    transition_table[state_counter]["transitions"][char] = next_node_counter
                    all_sets.add(frozenset(sorted(union_sigPos)))
                    next_node_counter += 1
                else:
                    # new state
                    print(f"There is already a set with the union positions {set(union_sigPos)}, ({state_counter},{char}) -> {union_sigPos} = {found_alias}")
                    transition_table[state_counter]["transitions"][char] = found_alias
            
            evaluated_sets.add(frozenset(selected_set))
            state_counter += 1

            print("\n")

        # acceptances states
        acceptance_states = {}
        for index, values in transition_table.items():
            accepting_for = [
                hashtag_id for hashtag_id, position in self.end_state.items() 
                if position in values["positions"]
            ]
            
            if accepting_for:
                acceptance_states[index] = accepting_for

        return self.clean_transition_table(transition_table), acceptance_states