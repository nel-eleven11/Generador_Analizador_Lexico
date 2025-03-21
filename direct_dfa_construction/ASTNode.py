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
        self.root: ASTNode = self.postfixToAst(postfix_expression)
        self.nextPosTable = {}
        self.alphabet = set()
        self.end_state = 0

    def postfixToAst(self, postfix):
        stack = []

        for char in postfix:
            if char.isalnum() or char == "ε" or char == "#":
                node = ASTNode(char)
                stack.append(node)
                print(f"Found {char}, pushing symbol to the stack")

            elif char in {'|', '~'}:
                right = stack.pop()
                left = stack.pop()
                node = ASTNode(char, left, right)
                stack.append(node)
                print(f"Found binary operator {char}, retrieving {right.value} and {left.value}, asigning them to the right and left childs respectively and pushing {char} to the stack")

            elif char == "*":
                left = stack.pop()
                node = ASTNode(char, left)
                stack.append(node)
                print(f"Found {char}, retrieving {left.value} and asigning it as left child, then char is pushed to the stack")

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

                if root.value not in ["ε", "*", "|", "~", "#"]:
                    self.alphabet.update([root.value])

                # Tis will initialize the table for next pos. So later we dont have to traverse the tree again.
                if root.value != "ε":
                    
                    self.nextPosTable[pos_counter[0]] = {'value': root.value, 'nextPos': set()}
                    pos_counter[0] += 1

                    # also here we adentify the number of the node that has #
                    if root.value == "#":
                        self.end_state = root.position
                    

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
        
    def nextPos_table_to_transition_table(self):

        # the table format is like this { 1: {'value': 'a', 'nextPos': {1,2,3}, ... }
        # this means that leaf 1 has a value of a and a nextPos set of {1,2,3}
        np_table = self.nextPosTable
        # states will have numbers as labels.
        state_counter = 0
        next_node_counter = 1

        # the ransition wil be a dictionary of dictionaries
        # the first key will be the number of the node and the value will be its transitions
        # so { 0: {positions:{1,2,3} transitions: {a: 2, b: 1} } } means state 0, has the positions {1,2,3} from the ast
        # and taht with "a" moves to state 2, and with "b" moves to state 1 (POSITIONS and states are not the same)
        transition_table = {}

        # where al subsets that we found are stored
        all_sets = set()
        #to check wich states we already evaluated
        evaluated_sets = set()

        # initial state is firstPos of root
        inital_set = self.root.firstPos
        all_sets.add(frozenset(inital_set))

        non_evaluated_sets = all_sets - evaluated_sets

        transition_table[state_counter] = {"positions": inital_set, "transitions": {}}

        while non_evaluated_sets != set():

            selected_set = next(iter(non_evaluated_sets))

            # for each letter in the alphabet
            for char in self.alphabet:

                print(f"Currently testing set {set(selected_set)}, with alphabet: {char}")

                union_sigPos = set()

                for position in selected_set:

                    if np_table[position]["value"] == char:
                        union_sigPos.update(np_table[position]["nextPos"])

                # Here is the point when a node does not have a transition with letter of the alphabet.
                # dead states can be implemented here also, but for simplicity of the DFA drawing we are skiping if the 
                # node does not have transitions with a specific alphabet letter
                if not union_sigPos:
                    print(f"No valid transition for ({state_counter},{char}) -> empty set")
                    continue 

                # now we have to check if said set already exists 

                found_alias = self.getAlias(transition_table, union_sigPos)

                if found_alias == "":

                    print(f"There is no set with positions {set(union_sigPos)}, ({state_counter},{char}) -> {union_sigPos} so we asign = {next_node_counter}")
                    #add transition to the tstae we are evaluating (1,a) -> 2, on state 1 with a we move to 2 for example
                    transition_table[state_counter]["positions"] = set(selected_set)
                    transition_table[state_counter]["transitions"][char] = next_node_counter

                    #adding the newly found set to our set of all sets
                    all_sets.add(frozenset(union_sigPos))
                    # now adding it to the transition table
                    transition_table[next_node_counter] = {"positions": set(union_sigPos), "transitions": {}}
                    #adding in case a new set is found
                    next_node_counter += 1
                
                else:
                    print(f"There is already a set with positions {set(union_sigPos)}, ({state_counter},{char}) -> {union_sigPos} = {found_alias}")
                    transition_table[state_counter]["transitions"][char] = int(found_alias)
                
            evaluated_sets.add(frozenset(selected_set))
            non_evaluated_sets = all_sets - evaluated_sets

            state_counter += 1

            print("\n")

        acceptance_states = set()

        for index, values in transition_table.items():
            print(index, values)

            for key, value in values.items():
                
                if self.end_state in values["positions"]:
                    print(index, "is acceptance")
                    acceptance_states.add(index)

                    break

        return transition_table, acceptance_states








