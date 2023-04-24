import heapq
import random
from collections import defaultdict

# --------------------------------------------------------------Class Node--------------------------------------------------------

class Node:
    
    def __init__(self, id, timestamp):
        ''''
        init function of the class Node
        '''
        self.id = id
        self.timestamp = timestamp
        self.children = []

    def add_child(self, child):
        '''
        add a child to the node
        '''
        self.children.append(child)

    def __repr__(self):
        return f"{self.id}, {self.timestamp}"

# --------------------------------------------------------------Print Tree---------------------------------------------------------------

def print_tree(tree, spaces=0):
    ''''
    function that print the tree as an horizontal tree
    if spaces are passed in input, the tree will be printed with the number of spaces passed in input
    '''
    print(" " * spaces, tree)
    for child in tree.children:
        print_tree(child, spaces+1)

# --------------------------------------------------------------Forward Simulation---------------------------------------------------------------

def forward_forest (seed_set, filename):
    '''
    Simulation of the infection to find the forest
    Input: graph and seedset
    Output: forest of infection
    '''

    # final forest of infection
    forest = list(Node(seed,-1) for seed in seed_set)
    infected = set(seed_set)

    # queue of tuples (src, message state)
    messages = defaultdict(list)

    last_unixts = None

    file = (row for row in open(filename, 'r'))
    filtered_edges = [(int(src), int(dst), int(unixts)) for src, dst, unixts in [line.split() for line in file] if int(dst) not in seed_set]

    for src, dst, unixts in filtered_edges:
        
        # check if the last_unixts is None or equal to the current unixts
        # if is equal, we'll continue to add elements on the queue
        # if is different, we'll clear the queue
        if last_unixts != None and last_unixts != unixts:
            create_infection_tree(messages, infected, last_unixts, forest)

        # if the src is infected, tthe message is infected
        if src in infected:
            state = 1
        else:
            state = 0

        # add the tuple (src, message state) to the queue
        # if if the destination is already in the list, we'll add the tuple to the queue
        messages[dst].append((src, state))

        last_unixts = unixts

    create_infection_tree(messages, infected, last_unixts, forest) # type: ignore
    return forest

def create_infection_tree (messages : dict[int, list[tuple[int, int]]], infected : set[int], last_unixts : int, forest : list[Node]):
    '''
    Input: the list of messages, the list of infected nodes, the last timestamp and the forest of infection
    Output: the forest of infection updated
    '''
    
    # messages is a dict[int, list[tuple[int, int]]]
    # the key int is the dst
    # the value list[tuple[int, int]] is a list of two value int:
    #   - the src
    #   - the state (infected or not)

    for (dst, data) in messages.items():
        if dst not in infected:
            # data is the list of (src, state)
            (_, state) = random.choice(data)
            if state == 1:
                # if an infected message is randomly chosen, we add the new node to the forest
                # as child of all the nodes that send an infected message to the new node
                new_node = Node(dst, last_unixts)
                add_infected_edges(new_node, infected, data, forest)
    messages.clear()


def add_infected_edges(node : Node, infected : set[int], list : list, forest : list[Node]):
    '''
    Input: the current node, the last timestamp, the list of infected nodes, the list of messages and the forest of infection
    Output: the forest of infection with the new edges
    '''

    # find the father of the node for each infected message
    for (src, state) in list:
        if state == 1:
            father_list = find_father(src, node.timestamp, forest)
            if father_list:
                for father in father_list:
                    father.add_child(node)
                    infected.add(node.id)

def find_father(id : int, timestamp : int, forest : list[Node]):
    '''
    function that takes in input the id of the node and the forest of infection
    and return the father of the node that will be the node that has the same id of the node passed in input
    and with the deepest level
    '''
    father = set()
    for tree in forest:
        dfs(tree, id, timestamp, father)
    return father

def dfs(tree : Node, id : int, timestamp : int, fathers : set[Node]):
    '''
    Input: the tree, the id of the node, the timestamp of the node and the list of the father
    Output: the fathers of the node that will be the node that has the same id of the node passed in input
    '''
    if tree.id == id and tree.timestamp < timestamp:
        # the take the node as possible father
        fathers.add(tree)
    for child in tree.children:
        dfs(child, id, timestamp, fathers)

# --------------------------------------------------------------Simulate Infection---------------------------------------------------------------

def simulate_infection (seed_set, filename, removed_nodes=[]):
    '''
    Spread the infection in the temporal network
    Input: seed is the seed set, filename is the name of the file
    Output: number of infected nodes
    '''

    infected = set(seed_set)

    # queue of tuples (src, message state)
    messages = defaultdict(list)

    last_unixts = None

    file = (row for row in open(filename, 'r'))
    filtered_edges = [(int(src), int(dst), int(unixts)) for src, dst, unixts in [line.split() for line in file] if int(src) not in removed_nodes and int(dst) not in removed_nodes]
    for src, dst, unixts in filtered_edges:

        # check if the last_unixts is None or equal to the current unixts
        # if is equal, we'll continue to add elements on the queue
        # if is different, we'll clear the queue
        if last_unixts != None and last_unixts != unixts:
            spread_infection(messages, infected)

        # if the src is infected, than the message is infected
        if src in infected:
            state = 1
        else:
            state = 0


        # add the tuple (src, message state) to the queue
        # if if the destination is already in the list, we'll add the tuple to the queue
        messages[dst].append(state)

        last_unixts = unixts
        
    spread_infection(messages, infected)
    return infected

def spread_infection (messages : dict[int, list[int]], infected : set[int]):
    '''
    Input: the list of messages and the list of infected nodes
    Output: the list of infected nodes updated
    '''
    
    # for each node that has received a message, choose a random message and check if it is infected
    for (dst, states) in messages.items():
        random_message = random.choice(states)
        if random_message == 1:
            infected.add(dst)
    messages.clear()

# --------------------------------------------------------------Choose Node---------------------------------------------------------------

def random_path (forest):
    '''
    Input: forest of infection
    Output: a random path in the forest
    '''
    path = []
    tree = random.choice(forest)
    path.append(tree)
    while tree.children != []:
        tree = random.choice(tree.children)
        path.append(tree)
    return path

def count_nodes (path : list[Node], nodes : dict[int, int], already_found : set[int]):
    '''
    Input: path, list of nodes and list of already found nodes
    Output: list of nodes updated
    '''
    for node in path:
        if node.id not in already_found:
            already_found.add(node.id)
            nodes[node.id] = 0
        nodes[node.id] += 1

def find_most_common_node (nodes: dict[int, int], budget: int):
    '''
    Input: list of nodes and budget
    Output: list of most common nodes
    '''
    top_nodes = {k: v for k, v in nodes.items() if v > 0}
    common_node_ids = [k for k, _ in heapq.nlargest(budget, top_nodes.items(), key=lambda x: x[1])]
    return set(common_node_ids)

# --------------------------------------------------------------Main---------------------------------------------------------------

if __name__ == "__main__":

    filename = "email.txt"

    seed_set = {83, 85} # seed set
    times = 100 # budget of nodes to remove
    node_budget = 3 # budget of nodes to remove
    nodes, already_found = {}, set() # list of nodes present in a random path and list of nodes already found in previous paths

    first_simulation = simulate_infection(seed_set, filename)
    print("first simulation: ", first_simulation)
    first_infected = len(first_simulation)

    for _ in range(times):

        # find the forest of infection
        forest = forward_forest(seed_set, filename)

        # choose a random path
        path = random_path(forest)

        if len(path) > 1:
            # remove the last node in order to not consider the leaf node that is useless for the infection
            path.pop(len(path) - 1)

            # remove the first node in order to not consider the root node that is a seed node and
            # it is not possible to remove a seed node
            path.pop(0)
    

        # count the nodes in the path
        count_nodes(path, nodes, already_found)

        forest.clear()

    print(nodes)

    # find the node with the highest number of times in the path
    common_node = find_most_common_node(nodes, node_budget)
    print("common node: ", common_node)

    # remove the node from the graph
    # we simulate the removal of the node by ignoring the edges that have the node as destination or source
    second_simulation = simulate_infection(seed_set, filename, common_node)

    print("second simulation: ", second_simulation)
    second_infected = len(second_simulation)
    
    ratio = second_infected / first_infected
    print("ratio: ", ratio)