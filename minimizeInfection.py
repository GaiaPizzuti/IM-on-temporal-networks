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
def find_father(id_node, id_timestamp, forest):
    father = None
    real_father = None
    max_depth = -1
    # for each tree in the forest
    for tree in forest:
        depth = 0
        last_depth = -1
        # find the node with the same id and the deepest level
        (father, max_depth) = dfs([], tree, id_node, id_timestamp, None, depth, max_depth)
        # if the father is not None and the depth is greater than the last depth
        if father != None and depth > last_depth:
            # update the father and the last depth
            last_depth = depth
            real_father = father
    return real_father

def dfs(visited, tree, id_node, id_timestamp, father, depth, max_depth):
    if tree not in visited:
        visited.append(tree)
        if tree.id == id_node and depth > max_depth and tree.timestamp < id_timestamp:
            father = tree
            max_depth = depth
        for child in tree.children:
            (father, max_depth) = dfs(visited, child, id_node, id_timestamp, father, depth+1, max_depth)
    return (father, max_depth)

        
def spread_infection (list_message, infected, last_unixts, forest):
    current_node = 0
    for list in list_message:
        # case in which the destination node is not infected
        if list != []:
            (own_src, message) = random.choice(list)
            if message == 1:
                new_node = Node(current_node, last_unixts)
                # find the father of the node
                father = find_father(own_src, last_unixts, forest)
                if father != None:
                    father.add_child(new_node)
                    if current_node not in infected:
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
                    spread_infection(list_message, infected, last_unixts, forest)
                
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

def find_longest_path(forest):
    longest_path = []
    for tree in forest:
        path = []
        dfs_path(tree, [], path)
        if len(path) > len(longest_path):
            longest_path = path
    return longest_path

def dfs_path (tree: Node, path : list[Node], result : list[Node]):
    path.append(tree)

    if not tree.children:
        if len(path) > len(result):
            result.clear()
            result.extend(path)
    else:
        for child in tree.children:
            dfs_path(child, path[:], result)


    

if __name__ == "__main__":
    seed_set = [0, 2]
    forest = simulateInfection(seed_set, "graph.txt")
    for tree in forest:
        print("tree:")
        print_tree(tree)
        print()

    longest_path = find_longest_path(forest)
    
    print("longest path:")
    for node in longest_path:
        node.print_node()
