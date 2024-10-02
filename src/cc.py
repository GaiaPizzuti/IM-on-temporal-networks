'''
file that define the cc function in order to control the number of cc contained in a graph before removing the attack set and after
removing it
'''

# ------------------------- class Node -------------------------

class Graph:
    # constructor
    def __init__(self, directed=True):
        self.directed = directed
        
        # initialize adjacency list
        self.adjacency_list = dict()
        
    def add_edge(self, src, dst):
        if not src in self.adjacency_list:
            self.adjacency_list[src] = set()
            
        self.adjacency_list[src].add(dst)
        
        if not dst in self.adjacency_list:
            self.adjacency_list[dst] = set()
        
        if not self.directed:
            self.adjacency_list[dst].add(src)
    
    def add_node(self, node):
        if not node in self.adjacency_list:
            self.adjacency_list[node] = set()


# ------------------------- functions -------------------------

def create_graph_from_file(filename: str, attack_set : list = []):
    G = Graph()
    with open(filename, 'r') as f:
        split_char = ' '
        if filename == 'data/fb-forum.txt':
            split_char = ','
        for line in f:
            src, dst, unixts = line.split(split_char)
            src, dst, unixts = int(src), int(dst), int(unixts)
            if src in attack_set:
                G.add_node(src)
            if dst in attack_set:
                G.add_node(dst)
            if src not in attack_set and dst not in attack_set:
                G.add_edge(src, dst)
    return G

def connected_components(filename: str, attack_set: list = []):
    '''
    function that count the number of cc in a graph
    
    input:
        - filename: str, the name of the file containing the information about the network
        - attack_set: list, list of nodes selected by the algorithm
    
    output:
        - counter: int, number of cc
    '''
    graph = create_graph_from_file(filename, attack_set)
    id = dict()
    for v in graph.adjacency_list.keys():
        id[v] = 0
    counter = 0
    for v in graph.adjacency_list.keys():
        if id[v] == 0:
            counter += 1
            cc_dfs(graph, counter, v, id)
    return counter, id

def cc_dfs(graph: Graph, counter: int, node: int, id: dict):
    '''
    function that count the number of cc in a graph
    
    input:
        - graph: Graph, the network of nodes
        - counter: int, number of the cc
        - node: int, node that is going to be analyzed
        - id: dict, dictionary saying each node from which component belong
    
    output: None
    '''
    id[node] = counter
    for v in graph.adjacency_list[node]:
        if id[v] == 0:
            cc_dfs(graph, counter, v, id)

def largest_component_size(id: dict):
    '''
    function that return the size of the largest component in the graphs
    
    input:
        - id: dict, dictionary that says each node from which component belongs
        
    output:
        - size of the largesest component
    '''
    sizes = dict()
    for value in id.values():
        if value not in sizes:
            sizes[value] = 0
        sizes[value] += 1
    
    return max(sizes.values())

def compare_cc(filename: str, attack_set_subtree: list, attack_set_centrality: list):
    '''
    function that print the number of connected components with the full graph, without the attack set from subtree algorithm and without the attack set from centrality algorithm
    
    input:
        - filename: str, the name of the file containing the information about the network
        - attack_set_subtree: list, list of nodes selected by the subtree algorithm
        - attack_set_centrality: list, list of nodes selected by the centrality algorithm
        
    output: None
    '''
    counter, ids = connected_components(filename)
    print('connected components in the full graph:', counter)
    
    largest_component_before = largest_component_size(ids)
    
    counter, ids_subtree = connected_components(filename, attack_set_subtree)
    print('connected components in the graph after removing the attack set with the subtree algorithm: ', counter)
    
    largest_subtree = largest_component_size(ids_subtree)
    
    counter, ids_centrality = connected_components(filename, attack_set_centrality)
    print('connected components in the graph after removing the attack set with the centrality algorithm: ', counter)
    
    largest_centrality = largest_component_size(ids_centrality)
    
    #print('ratio between largest cc before removing and after removing in the subtree: ', largest_subtree/largest_component_before)
    #print('ratio between largest cc before removing and after removing in the centrality: ', largest_centrality/largest_component_before)
    
    print()
    
    print('size largest cc before removing: ', largest_component_before)
    print('size largest cc after removing in subtree: ', largest_subtree)
    print('size largest cc after removing in centrality: ', largest_centrality)

if __name__ == '__main__':
    filename = 'data/email.txt'
    
    attack_set_subtree = [43, 88, 54, 25, 66, 80, 23, 48, 16, 35]
    attack_set_centrality = [54, 60, 71, 49, 25, 24, 48, 0, 26, 35]
    
    compare_cc(filename, attack_set_subtree, attack_set_centrality)