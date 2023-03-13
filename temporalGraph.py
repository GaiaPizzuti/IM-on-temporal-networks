import time
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
    

def create_graph_from_file(filename, window_size=1000):
    G = Graph()
    current_time = 0;
    with open(filename, 'r') as f:
        for line in f:
            src, dst, unixts = line.split()
            src, dst, unixts = int(src), int(dst), int(unixts)
            G.add_edge(src, dst, unixts=unixts)
            if current_time == window_size:
                break
            else:
                current_time += 1
    return G

# i need to create a graph for each window
# it's important to preserve each edge timestamp
def create_temporal_windows(filename, window_size=1000):
    graph_set = []
    current_time = 0
    with open(filename, 'r') as f:
        G = Graph()
        for line in f:
            src, dst, unixts = line.split()
            src, dst, unixts = int(src), int(dst), int(unixts)
            G.add_edge(src, dst, unixts=unixts)
            if current_time == window_size:
                current_time = 0
                graph_set.append(G)
                G = G.clear()
            else:
                current_time += 1
        graph_set.append(G)
    return graph_set



def spread_infection(seed, filename):
    '''
    Spread the infection in the temporal network
    Input: seed is the seed set, filename is the name of the file
    Output: number of infected nodes
    '''
    
    list_queue = []
    infected = seed
    last_unixts = None
    with open(filename, 'r') as f:
        for line in f:
            src, dst, unixts = line.split()
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
                        random_message = random.choice(list)
                        if random_message == 1:
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
            # for each node that has received a message, choose a random message and check if it is infected
            last_unixts = unixts
    
    return len(infected)

# find the seed set for the epidemic in a temporal graph
def find_seed_set(graph, k):
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

# ---------------------------- MAIN ----------------------------

if __name__ == "__main__":
    first_level = create_graph_from_file('CollegeMsg.txt')
    
    seed_set = find_seed_set(first_level, 30)
    print(seed_set)
    
    infected = spread_infection(seed_set, 'CollegeMsg.txt')
    print(infected)