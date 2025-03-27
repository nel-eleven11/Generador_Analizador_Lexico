from graphviz import Digraph

class AFDState:
    def __init__(self, state_number):
        self.state_number = state_number
        self.is_final = False
        self.transitions = {}
    def __repr__(self):
        return f"State({self.state_number})"

class DFA:
    def __init__(self, transition_table, acceptance_states, alphabet):
        self.states = {}
        self.start_state = None
        self.final_states = set()
        self.transition_table = self._clean_transition_table(transition_table)
        self.acceptance_states = acceptance_states
        self.alphabet = alphabet
        self._construct_dfa()

    def _clean_transition_table(self, transition_table):
        cleaned_table = {}
        for state_id, data in transition_table.items():
            cleaned_table[state_id] = {
                "transitions": {symbol: next(iter(target)) if isinstance(target, set) else target 
                                for symbol, target in data["transitions"].items()}
            }
        print("Cleaned table: ", cleaned_table)
        return cleaned_table

    def _construct_dfa(self):
        for state_id in self.transition_table:
            state = AFDState(state_id)
            if state_id in self.acceptance_states:
                state.is_final = True
                self.final_states.add(state)
            self.states[state_id] = state
            
        self.start_state = self.states[0]  # Assumption: initial state is always 0
        
        for state_id, transitions in self.transition_table.items():
            for symbol, target_id in transitions["transitions"].items():
                if isinstance(target_id, set):  # Ensure target_id is a single value
                    target_id = next(iter(target_id))
                self.states[state_id].transitions[symbol] = self.states.get(target_id, None)
        for state in self.states.values():
            print(state, state.state_number, state.transitions, state.is_final)

    def get_transitions(self):
        transitions = {}
        for state in self.states.values():
            state_num = state.state_number
            for char, target in state.transitions.items():
                if target is not None:
                    transitions[(state_num, char)] = target.state_number
        return transitions

    def get_start_state(self):
        return self.start_state.state_number if self.start_state else None

    def get_accept_states(self):
        return {state.state_number for state in self.final_states}

    def minimize(self):

        # Extraer la información necesaria
        transitions = self.get_transitions()         # Diccionario con claves: (estado, símbolo) -> estado destino
        start = self.get_start_state()                 # Estado inicial (número)
        accept_states = self.get_accept_states()       # Conjunto de estados aceptantes (números)
        all_states = list(self.states.keys())          # Lista de todos los estados del DFA
    
        # Inicializar la partición π₀: se separan los estados no aceptantes y aceptantes
        partitions = []
        non_accepting = [s for s in all_states if s not in accept_states]
        if non_accepting:
            partitions.append(non_accepting)
        if accept_states:
            partitions.append(list(accept_states))  
        # Obtener el alfabeto (símbolos) usado en las transiciones
        all_chars = sorted(list(set(char for (_, char) in transitions.keys())))
    
        # Refinamiento iterativo de las particiones
        while True:
            new_partitions = []
            for subset in partitions:
                group = {}  # Agrupar estados por su "firma" de transiciones
                for state in subset:
                    key = []
                    for char in all_chars:
                        if (state, char) in transitions:
                            dest = transitions[(state, char)]
                            # Buscar a qué partición pertenece 'dest'
                            index_dest = -1
                            for i, part in enumerate(partitions):
                                if dest in part:
                                    index_dest = i
                                    break
                            key.append(index_dest)
                        else:
                            key.append(-1)  # No existe transición para este símbolo
                    key = tuple(key)
                    group.setdefault(key, []).append(state)
                new_partitions.extend(list(group.values()))
            # Si la partición no cambió, hemos alcanzado la estabilidad
            if len(new_partitions) == len(partitions):
                break
            partitions = new_partitions

        # Asignar nuevos nombres a los estados de acuerdo a la partición
        new_state_mapping = {}
        new_id = 0
        # Se asigna el 0 a la partición que contiene al estado inicial
        for part in partitions:
            if start in part:
                for s in part:
                    new_state_mapping[s] = 0
                break
        # Asignar identificadores a las demás particiones
        for part in partitions:
            if start not in part:
                new_id += 1
                for s in part:
                    new_state_mapping[s] = new_id
    
        # Reconstruir la tabla de transiciones para el DFA minimizado
        new_transition_table = {}
        for (state, char), dest in transitions.items():
            new_src = new_state_mapping[state]
            new_dest = new_state_mapping[dest]
            if new_src not in new_transition_table:
                new_transition_table[new_src] = {"transitions": {}}
            new_transition_table[new_src]["transitions"][char] = new_dest
    
        # Asegurarse de que cada estado nuevo tenga una entrada en la tabla de transiciones
        for s in set(new_state_mapping.values()):
            if s not in new_transition_table:
                new_transition_table[s] = {"transitions": {}}
    
        # Definir los nuevos estados de aceptación y el estado inicial
        new_accept = set(new_state_mapping[s] for s in accept_states)
        new_start = new_state_mapping[start]
    
        # Retornar un nuevo DFA construido con la tabla minimizada, los estados aceptantes y el alfabeto original
        return DFA(new_transition_table, new_accept, self.alphabet)

    def verifyString(self, w):

        # A queue to show how the string is being consumed
        wordQueue = list(w)
        currentState = self.start_state
        currentTransitions = currentState.transitions

        print("\nChecking th String: ", w)

        for char in w:
            #Deleting the first element of the queue 
            print()
            print(f"Current state of the string: {wordQueue}, consuming: {char}")
            print("Current state: ", currentState)
            print("Avaiable transitions", currentTransitions)
            wordQueue.pop(0)
            currentStateCharTransitions = list(currentTransitions.keys())

            if char == "ε":
                print("No transition made, found ε character")

            elif char in currentStateCharTransitions:
                print(f"{currentState} has transition with: {char}")
                currentState = currentTransitions[char]
                print("Transitioning to state: ", currentState)
                currentTransitions = currentState.transitions
            
            else:
                print(f"{currentState} has no transitions with: {char}")
                return False
        
        #If the string makes it out of the loop, the entire string was consumed and we check if the state is final 
        if currentState.is_final:
            return True
        
        #If not return false
        return False


    def draw_dfa(self, filename):
        dot = Digraph()
        state_mapping = {}  # To map state numbers to node names in the Graphviz diagram

        # Create nodes for each state
        for state_alias in self.transition_table:
            state_name = f"State_{state_alias}"
            if state_alias in [state.state_number for state in self.final_states]:
                dot.node(state_name, label=str(state_alias), shape='doublecircle')
            else:
                dot.node(state_name, label=str(state_alias), shape='circle')
            state_mapping[state_alias] = state_name

        # Add edges for transitions
        for state_alias, transitions in self.transition_table.items():
            state_name = state_mapping[state_alias]
            for symbol, target_state in transitions["transitions"].items():
                if target_state != " ":  
                    target_state_name = state_mapping[target_state]
                    dot.edge(state_name, target_state_name, label=symbol)

        # Add an arrow pointing to the start state
        start_state_alias = self.start_state.state_number  # Get the alias of the start state (the number)
        start_state_name = state_mapping[start_state_alias]  # Now get the corresponding name in the Graphviz diagram
        dot.node('start', label='', shape='none', width='0', height='0')
        dot.edge('start', start_state_name)

        # Render the DFA to a file
        dot.render(filename, view=False)


__all__ = ["DFA"]

