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

    def print_node(self, spaces=0):
        for _ in range(spaces):
            print("  ", end="")
        print(self.id, self.timestamp)

    def print_children(self):
        for child in self.children:
            child.print_node()

# print the tree as a horizontal tree
def print_tree(tree, spaces=0):
    tree.print_node(spaces)
    for child in tree.children:
        print_tree(child, spaces+1)

    
# function that takes in input the id of the node and the forest of infection
# and return the father of the node that will be the node that has the same id of the node passed in input
# and with the deepest level
def find_father(id_node, timestamp, forest):
    father = []
    for tree in forest:
        dfs(tree, id_node, timestamp, father)
    return father

def dfs(tree : Node, id_node : int, timestamp : int, father : list[Node]):
    if tree.id == id_node and tree.timestamp < timestamp:
        # the take the node as possible father
        father.append(tree)
    for child in tree.children:
        dfs(child, id_node, timestamp, father)

def add_infected_edges(current_node : int, last_unixts: int, infected : list[int], list : list, forest : list[Node]):
    new_node = Node(current_node, last_unixts)
    # find the father of the node for each infected message
    for (src, state) in list:
        if state == 1:
            father_list = find_father(src, last_unixts, forest)
            if father_list != []:
                for father in father_list:
                    father.add_child(new_node)
                    if current_node not in infected:
                        infected.append(current_node)
            else:
                print("Error: father not found")

        
def create_infection_tree (list_message, infected, last_unixts, forest):
    current_node = 0
    for list in list_message:
        if list != []:
            (_, message) = random.choice(list)
            if message == 1:
                add_infected_edges(current_node, last_unixts, infected, list, forest)
        current_node += 1
    list_message.clear()

def spread_infection (list_message, infected):
    current_node = 0
    
    # for each node that has received a message, choose a random message and check if it is infected
    for list in list_message:
        if list != [] and current_node not in infected:
            random_message = random.choice(list)
            if random_message == 1:
                infected.append(current_node)
        current_node += 1
    list_message.clear()

def forward_forest (seed_set, filename):
    '''
    Simulation of the infection to find the forest
    Input: graph and seedset
    Output: forest of infection
    '''

    # final forest of infection
    forest = []
    infected = []
    for seed in seed_set:
        forest.append(Node(seed, -1))
        infected.append(seed)

    # queue of tuples (src, message state)
    list_message = []

    last_unixts = None

    with open(filename, 'r') as f:
        for line in f:
            src, dst, unixts = line.split()
            src, dst, unixts = int(src), int(dst), int(unixts)

            # if the destination node is a seed, we do not have interest in adding it to the queue
            if dst not in seed_set:
                
                # if the src is infected, tthe message is infected
                if src in infected:
                    state = 1
                else:
                    state = 0
                
                # check if the last_unixts is None or equal to the current unixts
                # if is equal, we'll continue to add elements on the queue
                # if is different, we'll clear the queue
                if last_unixts != None and last_unixts != unixts:
                    create_infection_tree(list_message, infected, last_unixts, forest)

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
        

    create_infection_tree(list_message, infected, last_unixts, forest)
    return forest

def simulate_infection (seed_set, filename, removed_nodes=[]):
    '''
    Spread the infection in the temporal network
    Input: seed is the seed set, filename is the name of the file
    Output: number of infected nodes
    '''

    infected = []
    for seed in seed_set:
        infected.append(seed)

    # queue of tuples (src, message state)
    list_message = []

    last_unixts = None

    with open(filename, 'r') as f:
        for line in f:
            src, dst, unixts = line.split()
            src, dst, unixts = int(src), int(dst), int(unixts)

            # if the source node is a node that has been removed, we have to skip the line
            if src not in removed_nodes and dst not in removed_nodes:

                # if the src is infected, than the message is infected
                if src in infected:
                    state = 1
                else:
                    state = 0
                
                # check if the last_unixts is None or equal to the current unixts
                # if is equal, we'll continue to add elements on the queue
                # if is different, we'll clear the queue
                if last_unixts != None and last_unixts != unixts:
                    spread_infection(list_message, infected)

                # add the tuple (src, message state) to the queue
                # if if the destination is already in the list, we'll add the tuple to the queue
                if len(list_message) > dst:
                    list_message[dst].append(state)
                else:
                    # else create a new queue
                    queue = []
                    queue.append(state)
                    if len(list_message) <= dst:
                        for _ in range(dst - len(list_message) + 1):
                            list_message.append([])
                    list_message[dst] = queue

                last_unixts = unixts
        
    spread_infection(list_message, infected)
    return infected

def random_path (forest):
    path = []
    tree = random.choice(forest)
    path.append(tree)
    while tree.children != []:
        tree = random.choice(tree.children)
        path.append(tree)
    return path

def count_nodes (path : list[Node], nodes : list[int], already_found : list[int]):
    for node in path:
        if node.id not in already_found:
            already_found.append(node.id)
            if len(nodes) <= node.id:
                for _ in range(node.id - len(nodes) + 1):
                    nodes.append(0)
        nodes[node.id] += 1

def find_most_common_node (nodes: list[int], budget: int):
    common_node = []
    for _ in range(budget):
        max = 0
        for node in range(len(nodes)):
            if nodes[node] > max and node not in common_node:
                max = nodes[node]
                common_node.append(node)
    return common_node



if __name__ == "__main__":

    seed_set = [0] # seed set
    times = 10 # budget of nodes to remove
    node_budget = 1 # budget of nodes to remove
    nodes, already_found = [], [] # list of nodes present in a random path and list of nodes already found in previous paths

    first_simulation = simulate_infection(seed_set, "graph.txt")

    for _ in range(times):

        # find the forest of infection
        forest = forward_forest(seed_set, "graph.txt")

        for tree in forest:
            print("tree:")
            print_tree(tree)
            print()

        # choose a random path
        path = random_path(forest)

        print("path:")
        for node in path:
            node.print_node()

        # remove the last node in order to not consider the leaf node that is useless for the infection
        path.pop(len(path) - 1)

        # remove the first node in order to not consider the root node that is a seed node and
        # it is not possible to remove a seed node
        path.pop(0)
    

        # count the nodes in the path
        count_nodes(path, nodes, already_found)

        print(nodes)

        forest.clear()

    # find the node with the highest number of times in the path
    common_node = find_most_common_node(nodes, node_budget)

    # remove the node from the graph
    # we simulate the removal of the node by ignoring the edges that have the node as destination or source
    second_simulation = simulate_infection(seed_set, "graph.txt", common_node)

    print("first simulation: ", first_simulation)
    print("second simulation: ", second_simulation)
    
    ratio = len(second_simulation) / len(first_simulation)
    print("ratio: ", ratio)