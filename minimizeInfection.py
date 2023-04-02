# define a function that takes in input graph, seed set, budget of nodes/edges
# and return in output the list of nodes that we have to delete to minimize the infection

# the function is divided in two parts:
# - a function that takes in input the seed set and return a forest of infection and choose a path for n times
# - a function that takes in input the paths and the budget and
#   count the number of total repetition of a node in every paths and choose the nodes to delete

# we had to see the graph as a tree in which each node is a tuple (node, timestamp)

import random


class Graph:
    # constructor
    def __init__(self):

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

class Node:
    # constructor
    def __init__(self, id, timestamp):
        # each node has an id and a timestamp
        # tuple (id, timestamp)
        self.id = id
        self.timestamp = timestamp
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def print_node(self):
        print(self.id, self.timestamp)

def print_tree(tree):
    tree.print_node()
    for child in tree.children:
        print_tree(child)
    

def find_father(id_node, tree):
    for node in tree:
        if node.id == id_node:
            return node
        elif node.children != []:
                return find_father(id_node, node.children)
        else:
            return None
        
def spread_infection (list_message, infected, last_unixts, forest):
    current_node = 0
    print("list_message: ", list_message)
    for list in list_message:
        if list != [] and current_node not in infected:
            (own_src, message) = random.choice(list)
            print ("src: ", own_src, "message: ", message)
            if message == 1:
                new_node = Node(current_node, last_unixts)
                # find the father of the node
                father = find_father(own_src, forest)
                if father != None:
                    father.add_child(new_node)
                    infected.append(current_node)
                else:
                    print("Error: father not found")
        current_node += 1
    list_message.clear()
        
    

def simulateInfection (seed_set, filename):
    '''
    Simulation of the infection to find the forest
    Input: graph and seedset
    Output: forest of infection
    '''

    # final forest of infection
    forest = []
    for seed in seed_set:
        forest.append(Node(seed, -1))

    # queue of tuples (src, message state)
    list_message = []

    infected = seed_set
    last_unixts = None

    with open(filename, 'r') as f:
        for line in f:
            src, dst, unixts = line.split()
            src, dst, unixts = int(src), int(dst), int(unixts)
            
            # if the src is infected, tthe message is infected
            if src in infected:
                state = 1
            else:
                state = 0
            
            # check if the last_unixts is None or equal to the current unixts
            # if is equal, we'll continue to add elements on the queue
            # if is different, we'll clear the queue
            if last_unixts != None and last_unixts != unixts:
                spread_infection(list_message, infected, last_unixts, forest)

            print("src: ", src, "dst: ", dst, "unixts: ", unixts)
            
            # add the tuple (src, message state) to the queue
            # if if the destination is already in the list, we'll add the tuple to the queue
            if len(list_message) > dst:
                list_message[dst].append((src, state))
            else:
                # else create a new queue
                queue = []
                queue.append((src, state))
                if len(list_message) <= dst:
                    for _ in range(dst - len(list_message) + 1):
                        list_message.append([])
                list_message[dst] = queue

            last_unixts = unixts
    

    spread_infection(list_message, infected, last_unixts, forest)
    return forest

if __name__ == "__main__":
    seed_set = [0]
    forest = simulateInfection(seed_set, "graph.txt")
    for tree in forest:
        print_tree(tree)
