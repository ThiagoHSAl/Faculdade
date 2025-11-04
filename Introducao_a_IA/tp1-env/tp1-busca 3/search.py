import heapq
from math import sqrt
from collections import deque

WALL = 'X'
START_STATE = 'S'
GOAL_STATE  = 'G'

def plan(map, algorithm='bfs', heuristic=None):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """
    print(map)
    print("Algorithm:", algorithm)
    print("Heuristic:", heuristic)

    # Load the level from the file
    level = parse_level(map)

    # Retrieve the source and destination coordinates from the level.
    start = level['start']
    goal = level['goal']

    # Search for and display the path from src to dst.
    path = []
    visited = {}

    if algorithm == 'bfs':
        path, visited = bfs(start, goal, level, transition_model)
    elif algorithm == 'dfs':
        path, visited = dfs(start, goal, level, transition_model)
    elif algorithm == 'ucs':
        path, visited = ucs(start, goal, level, transition_model)
    elif algorithm == 'greedy':
        if heuristic == 'euclidian':
            path, visited = greedy_best_first(start, goal, level, transition_model, h_euclidian)
        elif heuristic == 'manhattan':
            path, visited = greedy_best_first(start, goal, level, transition_model, h_manhattan)
    elif algorithm == 'astar':
        if heuristic == 'euclidian':
            path, visited = a_star(start, goal, level, transition_model, h_euclidian)
        elif heuristic == 'manhattan':
            path, visited = a_star(start, goal, level, transition_model, h_manhattan)

    return path, path_cost(path, level), visited

def parse_level(map):
    """ Parses a level from a string.

    Args:
        level_str: A string containing a level.

    Returns:
        The parsed level (dict) containing the locations of walls (set), the locations of spaces 
        (dict), and a mapping of locations to waypoints (dict).
    """
    start = None
    goal = None
    walls = set()
    spaces = {}

    for j, line in enumerate(map.split('\n')):
        for i, char in enumerate(line):
            if char == '\n':
                continue
            elif char == WALL:
                walls.add((i, j))
            elif char == START_STATE:
                start = (i, j)
                spaces[(i, j)] = 1.
            elif char == GOAL_STATE:
                goal = (i, j) 
                spaces[(i, j)] = 1.
            elif char.isnumeric():
                spaces[(i, j)] = float(char)

    level = {'walls': walls, 'spaces': spaces, 'start': start, 'goal': goal}

    return level

def path_cost(path, level):
    """ Returns the cost of the given path.

    Args:
        path: A list of cells from the source to the goal.
        level: A loaded level, containing walls, spaces, and waypoints.

    Returns:
        The cost of the given path.
    """
    cost = 0
    for i in range(len(path) - 1):
        cost += cost_function(level, path[i], path[i + 1], 
                              level['spaces'][path[i]], 
                              level['spaces'][path[i + 1]])

    return cost

# =============================
# Transition Model
# =============================

def cost_function(level, state1, state2, cost1, cost2):
    """ Returns the cost of the edge joining state1 and state2.

    Args:
        state1: A source location.
        state2: A target location.

    Returns:
        The cost of the edge joining state1 and state2.
    """

    ################################
    # 1.1 INSIRA SEU CÓDIGO AQUI
    ################################
    x1, y1 = state1
    x2, y2 = state2
    
    # Calcula a distância euclidiana
    dist = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Calcula o custo médio dos espaços
    avg_cost = (cost1 + cost2) / 2
    
    return dist * avg_cost

def transition_model(level, state1):
    """ Provides a list of adjacent states and their respective costs from the given state.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        state: A target location.

    Returns:
        A list of tuples containing an adjacent sates's coordinates and the cost of 
        the edge joining it and the originating state.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """
    adj_states = {}
    ################################
    # 1.2 INSIRA SEU CÓDIGO AQUI
    ################################
    x, y = state1
    # Itera sobre os 8 vizinhos possíveis (incluindo diagonais)
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            neighbor_state = (i, j)
            
            # Pula o próprio estado
            if neighbor_state == state1:
                continue

            # Verifica se o vizinho não é uma parede e é um espaço válido
            if neighbor_state not in level['walls'] and neighbor_state in level['spaces']:
                cost1 = level['spaces'][state1]
                cost2 = level['spaces'][neighbor_state]
                
                # Calcula o custo de transição
                transition_cost = cost_function(level, state1, neighbor_state, cost1, cost2)
                adj_states[neighbor_state] = transition_cost

    return adj_states.items()

# =============================
# Uninformed Search Algorithms
# =============================

def bfs(s, g, level, adj):
    """ Searches for a path from the source to the goal using the Breadth-First Search algorithm.

    Args:
        s: The source location.
        g: The goal location.
        level: The level containing the locations of walls, spaces, and waypoints.
        adj: A function that returns the adjacent cells and their respective costs from the given cell.

    Returns:
        A list of tuples containing cells from the source to the goal, and a dictionary 
        containing the visited cells and their respective parent cells.
    """
    visited = {s: None}

    ################################
    # 2.1 INSIRA SEU CÓDIGO AQUI
    ################################

    # 1. Inicializa a fila com o estado inicial
    queue = deque([s])

    # 2. Loop principal: continua enquanto houver nós para explorar na fila
    while queue:
        # 3. Retira o próximo nó da fila (o mais antigo)
        current_node = queue.popleft()

        # 4. Verifica se alcançou o objetivo
        if current_node == g:
            # Se sim, reconstrói o caminho de volta para a origem
            path = []
            step = g
            while step is not None:
                path.insert(0, step) # Insere no início para inverter a ordem
                step = visited[step] # Move para o "pai" do nó atual
            return path, visited

        # 5. Obtém os vizinhos do nó atual
        for neighbor, cost in adj(level, current_node):
            # 6. Para cada vizinho, verifica se já foi visitado
            if neighbor not in visited:
                # Se não foi, marca como visitado, registrando o nó atual como seu "pai"
                visited[neighbor] = current_node
                # Adiciona o vizinho à fila para ser explorado depois
                queue.append(neighbor)

    # 7. Se a fila esvaziar e o objetivo não for encontrado, não há caminho
    return [], visited

def dfs(s, g, level, adj):
    """ Searches for a path from the source to the goal using the Depth-First Search algorithm.
    Args:
        s: The source location.
        g: The goal location.
        level: The level containing the locations of walls, spaces, and waypoints.
        adj: A function that returns the adjacent cells and their respective costs from the given cell.
    
    Returns:
        A list of tuples containing cells from the source to the goal, and a dictionary containing the visited cells and their respective parent cells.
    """
    visited = {s: None}

    ################################
    # 2.2 INSIRA SEU CÓDIGO AQUI
    ################################

    # 1. Inicializa a pilha com o estado inicial
    stack = [s]

    # 2. Loop principal: continua enquanto houver nós para explorar na pilha
    while stack:
        # 3. Retira o próximo nó da pilha (o mais recente)
        current_node = stack.pop()

        # 4. Verifica se alcançou o objetivo
        if current_node == g:
            # Se sim, reconstrói o caminho de volta para a origem
            path = []
            step = g
            while step is not None:
                path.insert(0, step) # Insere no início para inverter a ordem
                step = visited[step] # Move para o "pai" do nó atual
            return path, visited

        # 5. Obtém os vizinhos do nó atual
        for neighbor, cost in adj(level, current_node):
            # 6. Para cada vizinho, verifica se já foi visitado
            if neighbor not in visited:
                # Se não foi, marca como visitado, registrando o nó atual como seu "pai"
                visited[neighbor] = current_node
                # Adiciona o vizinho à pilha para ser o próximo a ser explorado
                stack.append(neighbor)

    # 7. Se a pilha esvaziar e o objetivo não for encontrado, não há caminho
    return [], visited

def ucs(s, g, level, adj):
    """ Searches for a path from the source to the goal using the Uniform-Cost Search algorithm.

    Args:
        s: The source location.
        g: The goal location.
        level: The level containing the locations of walls, spaces, and waypoints.
        adj: A function that returns the adjacent cells and their respective costs from the given cell.

    Returns:
        A list of tuples containing cells from the source to the goal, and a dictionary containing the visited cells and their respective parent cells.
    """
    visited = {s: None}

    ################################
    # 2.3 INSIRA SEU CÓDIGO AQUI
    ################################

    # 1. Começamos com o nó inicial 's', que tem custo 0 para ser alcançado.
    priority_queue = [(0, s)]
    
    # 2. Dicionário para rastrear o menor custo encontrado até agora para cada nó.
    cost_so_far = {s: 0}

    # 3. Loop principal: continua enquanto houver nós na fila de prioridade.
    while priority_queue:
        # 4. Retira o nó com o MENOR custo da fila.
        current_cost, current_node = heapq.heappop(priority_queue)

        # 5. Se alcançamos o objetivo, terminamos!
        if current_node == g:
            path = []
            step = g
            while step is not None:
                path.insert(0, step)
                step = visited[step]
            return path, visited

        # 6. Para cada vizinho do nó atual...
        for neighbor, transition_cost in adj(level, current_node):
            # 7. Calcula o novo custo para chegar a este vizinho através do nó atual.
            new_cost = cost_so_far[current_node] + transition_cost
            
            # 8. Se o vizinho ainda não foi visitado, OU se encontramos um caminho
            # MAIS BARATO para ele, atualizamos as informações.
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                # Atualiza o menor custo para chegar ao vizinho
                cost_so_far[neighbor] = new_cost
                # Registra que chegamos a este vizinho a partir do nó atual
                visited[neighbor] = current_node
                # Adiciona o vizinho à fila de prioridade com seu novo custo
                heapq.heappush(priority_queue, (new_cost, neighbor))

    # 9. Se a fila esvaziar e não chegamos ao objetivo, não há caminho.
    return [], visited

# ======================================
# Informed (Heuristic) Search Algorithms
# ======================================
def greedy_best_first(s, g, level, adj, h):
    """ Searches for a path from the source to the goal using the Greedy Best-First Search algorithm.
    
    Args:
        s: The source location.
        g: The goal location.
        level: The level containing the locations of walls, spaces, and waypoints.
        adj: A function that returns the adjacent cells and their respective costs from the given cell.
        h: A heuristic function that estimates the cost from the current cell to the goal.

    Returns:
        A list of tuples containing cells from the source to the goal, and a dictionary containing the visited cells and their respective parent cells.
    """
    visited = {s: None}

    ################################
    # 3.2 INSIRA SEU CÓDIGO AQUI
    ################################

    # 1. A prioridade é a estimativa da distância de 's' até 'g'.
    priority_queue = [(h(s, g), s)]
    
    # 2. Loop principal: continua enquanto houver nós na fila.
    while priority_queue:
        # 3. Retira o nó com a MENOR estimativa heurística (o que parece estar mais perto do fim).
        heuristic_value, current_node = heapq.heappop(priority_queue)

        # 4. Se alcançamos o objetivo, terminamos.
        if current_node == g:
            path = []
            step = g
            while step is not None:
                path.insert(0, step)
                step = visited[step]
            return path, visited

        # 5. Para cada vizinho do nó atual...
        for neighbor, transition_cost in adj(level, current_node):
            # 6. Se o vizinho ainda não foi visitado...
            if neighbor not in visited:
                # Marca como visitado e define seu "pai"
                visited[neighbor] = current_node
                # Calcula a prioridade do vizinho usando a heurística
                priority = h(neighbor, g)
                # Adiciona o vizinho à fila de prioridade
                heapq.heappush(priority_queue, (priority, neighbor))

    # 7. Se a fila esvaziar, não há caminho.
    return [], visited

def a_star(s, g, level, adj, h):
    """ Searches for a path from the source to the goal using the A* algorithm.

    Args:
        s: The source location.
        g: The goal location.
        level: The level containing the locations of walls, spaces, and waypoints.
        adj: A function that returns the adjacent cells and their respective costs from the given cell.
        h: A heuristic function that estimates the cost from the current cell to the goal.
    
    Returns:
        A list of tuples containing cells from the source to the goal, and a dictionary containing the visited cells and their respective parent cells.
    """
    visited = {s: None}

    ################################
    # 3.3 INSIRA SEU CÓDIGO AQUI
    ################################
    # 1. Dicionário para rastrear o custo real do caminho da origem até cada nó (g(n)).
    g_score = {s: 0}
    
    # 2. Para o nó inicial, g_score é 0, então f_score = h(s, g).
    f_score = h(s, g)
    priority_queue = [(f_score, s)]
    
    # 3. Loop principal: continua enquanto houver nós na fila.
    while priority_queue:
        # 4. Retira o nó com o MENOR f_score da fila.
        current_f_score, current_node = heapq.heappop(priority_queue)
        
        # 5. Se alcançamos o objetivo, terminamos.
        if current_node == g:
            path = []
            step = g
            while step is not None:
                path.insert(0, step)
                step = visited[step]
            return path, visited
        
        # 6. Para cada vizinho do nó atual...
        for neighbor, transition_cost in adj(level, current_node):
            # 7. Calcula o g_score (custo real) para chegar a este vizinho.
            tentative_g_score = g_score[current_node] + transition_cost
            
            # 8. Se o vizinho ainda não foi visitado, OU se encontramos um caminho
            # mais barato para ele (menor g_score)...
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                # Atualiza o "pai" e o g_score
                visited[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                
                # Calcula o f_score do vizinho
                new_f_score = tentative_g_score + h(neighbor, g)
                
                # Adiciona o vizinho à fila de prioridade com seu f_score
                heapq.heappush(priority_queue, (new_f_score, neighbor))

    # 9. Se a fila esvaziar, não há caminho.
    return [], visited

# ======================================
# Heuristic functions
# ======================================
def h_euclidian(s, g):
    """ Estimates the cost from the current cell to the goal using the Euclidian distance.

    Args:
        s: The current location.
        g: The goal location.
    
    Returns:
        The estimated cost from the current cell to the goal.    
    """

    ################################
    # 3.1 INSIRA SEU CÓDIGO AQUI
    ################################
    x1, y1 = s
    x2, y2 = g
    
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def h_manhattan(s, g):
    """ Estimates the cost from the current cell to the goal using the Manhattan distance.
    
    Args:
        s: The current location.
        g: The goal location.
    
    Returns:
        The estimated cost from the current cell to the goal.
    """

    ################################
    # 3.1 INSIRA SEU CÓDIGO AQUI
    ################################
    x1, y1 = s
    x2, y2 = g

    return abs(x2 - x1) + abs(y2 - y1)