import random

# creation of a graph from a file
# data format -> src dst unixts
# src: id of the source node
# dst: id of the target node
# unixts: unix timestamp of the edge

# the timestamp is the time when the edge is present
# when a message is sent, it can be infected or not
# the message will be stored in a queue per node
# timestamp are ordered

PROB_OF_BEING_INFECTED = 0.2
'''
probability of not being infected: (1 - PROB_OF_BEING_INFECTED)^(number_of_infected_messages)
'''

class Graph:
    # constructor
    def __init__(self, directed=True):
        self.directed = directed
        
        # initialize adjacency list
        # create a matrix with 'nodes' rows and columns
        self.adjacency_list = []
        
    def add_edge(self, src, dst, unixts=1):
        #self.adjacency_list.update({src: {dst: unixts}})
        if len(self.adjacency_list) <= src:
            for _ in range(src - len(self.adjacency_list) + 1):
                self.adjacency_list.append([])
        
        if len(self.adjacency_list[src]) <= dst:
            for _ in range(dst - len(self.adjacency_list[src]) + 1):
                self.adjacency_list[src].append([])
                
        self.adjacency_list[src][dst].append(unixts)
        
        if not self.directed:
            if len(self.adjacency_list) <= dst:
                for _ in range(dst - len(self.adjacency_list) + 1):
                    self.adjacency_list.append([])
        
            if len(self.adjacency_list[dst]) <= src:
                for _ in range(src - len(self.adjacency_list[dst]) + 1):
                    self.adjacency_list[dst].append([])
                    
            self.adjacency_list[dst][src].append(unixts)
    
    def print_graph(self):
        for src in range (len(self.adjacency_list)):
            for dst in range (len(self.adjacency_list[src])):
                if self.adjacency_list[src][dst] != []:
                    print(src, dst, self.adjacency_list[src][dst])
    
    def clear(self):
        return Graph()
    
    def get_nodes(self):
        return set(range(len(self.adjacency_list)))
    
    def get_node_degree(self, node):
        edges = 0
        for dst in range (len(self.adjacency_list[node])):
            if self.adjacency_list[node][dst] != []:
                edges += 1
        return edges

# i need to create a graph for each window
# it's important to preserve each edge timestamp
def create_temporal_windows(filename, window_size=1000):
    graph_set = []
    current_time = 0
    last_unixts = None
    with open(filename, 'r') as f:
        G = Graph()
        split_char = ' '
        if filename == 'data/fb-forum.txt':
            split_char = ','
        for line in f:
            src, dst, unixts = line.split(split_char)
            src, dst, unixts = int(src), int(dst), int(unixts)
            G.add_edge(src, dst, unixts=unixts)
            if last_unixts != None and last_unixts != unixts:
                if current_time == window_size:
                    current_time = 0
                    graph_set.append(G)
                    G = G.clear()
                else:
                    current_time += 1
            last_unixts = unixts
        graph_set.append(G)
    return graph_set



def spread_infection(seed, filename, prob: float):
    '''
    Spread the infection in the temporal network
    Input: seed is the seed set, filename is the name of the file
    Output: number of infected nodes
    '''
    
    list_queue = []
    infected = seed
    last_unixts = None
    with open(filename, 'r') as f:
        split_char = ' '
        if filename == 'data/fb-forum.txt':
            split_char = ','
        for line in f:
            src, dst, unixts = line.split(split_char)
            src, dst, unixts = int(src), int(dst), int(unixts)
            
            # if the source of the message is infected, the message is infected too
            if src in infected:
                state = 1
            else :
                state = 0
            
            # check if the last_unixts is none or equal to unixts
            # if is equal, we'll continue to add element on the queue
            # if is None or different, clear the queue
            if last_unixts != None and last_unixts != unixts:
                current_node = 0
                
                for list in list_queue:
                    if list != [] and current_node not in infected:
                        """
                        proviouse version in which we used to choose a random message and check if it was infected
                        random_message = random.choice(list)
                        if random_message == 1:
                            infected.append(current_node) """
                            
                        # probability of not being infected is equal to (1 - PROB_OF_BEING_INFECTED)^(INFECTED_MESSAGES)
                        infected_messages = sum(list)
                        prob_of_not_being_infected = pow((1 - prob), infected_messages)
                        result_infection = random.uniform(0, 1)
                        # if the obtained result is greater than the probability of not being infected then the nose is infected
                        if (result_infection > prob_of_not_being_infected):
                            infected.append(current_node)
                    current_node += 1
                list_queue.clear()
            
            # add the message to the destination queue
            # if the destination is already in the list, add the message to the queue
            if len(list_queue) > dst:
                list_queue[dst].append(state)
            else:
                # else create a new queue
                queue = []
                queue.append(state)
                if len(list_queue) <= dst:
                        for _ in range(dst - len(list_queue) + 1):
                            list_queue.append([])
                list_queue[dst] = queue 
            
            last_unixts = unixts
    
    return len(infected)

# find the seed set for the epidemic in a temporal graph
def find_seed_set(graph, k=1):
    '''
    Greedy algorithm for finding the seed set
    Input: graph is a graph, k is the number of nodes to be selected
    Output: seed set
    '''
    S = []
    
    for _ in range(k):
        best_degree = 0
        node = None
        for v in graph.get_nodes() - set(S):
            
            # get the degree of the node
            degree = graph.get_node_degree(v)
            
            # update the winning node and spread so far
            if degree > best_degree:
                best_degree, node = degree, v
                
        # add the selected node to the seed set
        S.append(node)
        
    return S

def influence_maximization(filename: str, prob: float = PROB_OF_BEING_INFECTED):
    windows = create_temporal_windows(filename)
    seed_set = []
    for window in windows:
        if find_seed_set(window)[0] not in seed_set:
            seed_set.append(find_seed_set(window)[0])
    return seed_set

# ---------------------------- MAIN ----------------------------

if __name__ == "__main__":
    filename = 'data/email.txt'
    seed = influence_maximization(filename)
    print(seed)