# ------------------------- class Node -------------------------

from collections import defaultdict
import random
import igraph as ig
from matplotlib import patches
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from operator import itemgetter

class Node:
    
    def __init__(self, id, timestamp):
        ''''
        init function of the class Node
        '''
        self.id = id
        self.timestamp = timestamp
        self.children = []
        self.subtree_size = 0

    def add_child(self, child):
        '''
        add a child to the node
        '''
        self.children.append(child)

    def __repr__(self):
        return f"{self.id}, {self.timestamp}"
    
# ------------------------ print tree ------------------------

def print_tree(tree, spaces=0):
    ''''
    function that print the tree as an horizontal tree
    if spaces are passed in input, the tree will be printed with the number of spaces passed in input
    '''
    print(" " * spaces, tree)
    for child in tree.children:
        print_tree(child, spaces+1)

# ------------------------- functions -------------------------

def simulate_infection(seed_set : set, filename : str, removed_nodes=[], nodes=[]) -> set[int]:
    '''
    simulate the infection of a graph
    input: seed_set is the set of original infected nodes, filename is the name of the file containing the graph
    output: the number of infected nodes
    '''
    
    infected = set(seed_set)

    # queue of tuples (src, state)
    messages = defaultdict(list)

    last_unixts = None

    file = (row for row in open(filename, "r"))
    filtered_edges = [(int(src), int(dst), int(unixts)) for src, dst, unixts in [line.split() for line in file] if int(src) not in removed_nodes and int(dst) not in removed_nodes]
    for src, dst, unixts in filtered_edges:

        if removed_nodes == []:
            count_nodes(src, dst, nodes)

        # check if the last_unixts is None or queal to the current unixts
        # if is equal, we'll continue to add elements to the queue
        # if is different, we'll process the queue
        if last_unixts != None and last_unixts != unixts:
            process_queue (messages, infected)

        # if the src is infected, than the message is infected
        if src in infected:
            state = 1
        else:
            state = 0

        # add the tuple (src, state) to the queue
        # if the destination is already in the list, we'll add the tuple to the queue
        messages[dst].append(state)

        last_unixts = unixts

    process_queue (messages, infected)
    return infected

def process_queue (messages : dict[int, list[int]], infected : set[int]):
    '''
    function that process the queue of messages: it choose a random message from the queue and
    if the message is infected, it will added to the infection tree
    input: messages is the queue of messages, infected is the set of infected nodes
    output: it doesn't return anything, it just update the set of infected nodes
    '''

    # for each node that has received a message, choose a random message from the queue and check if it is infected
    for dst, states in messages.items():
        random_state = random.choice(states)
        if random_state == 1:
            infected.add(dst)
    messages.clear()

# ------------------------- forward forest -------------------------

def forward_forest (seed_set : set, filename : str) -> list[Node]:
    '''
    Simulation of the infection to find the forest of the infection
    input: seed_set is the set of original infected nodes, filename is the name of the file containing the graph
    output: the forest of the infection
    '''

    # final forest of the infection
    forest = list(Node(seed, -1) for seed in seed_set)
    infected = set(seed_set)

    # queue of tuples (src, state)
    messages = defaultdict(list)

    last_unixts = None

    file = (row for row in open(filename, "r"))
    filtered_edges = [(int(src), int(dst), int(unixts)) for src, dst, unixts in [line.split() for line in file] if int(dst) not in seed_set]

    for src, dst, unixts in filtered_edges:

        # check if the last_unixts is None or queal to the current unixts
        # if is equal, we'll continue to add elements to the queue
        # if is different, we'll process the queue
        if last_unixts != None and last_unixts != unixts:
            update_infection_tree (messages, infected, forest, last_unixts)
        
        # if the src is infected, than the message is infected
        if src in infected:
            state = 1
        else:
            state = 0
        
        # add the tuple (src, state) to the queue
        # if the destination is already in the list, we'll add the tuple to the queue
        messages[dst].append((src, state))

        last_unixts = unixts

    update_infection_tree (messages, infected, forest, last_unixts) # type: ignore
    return forest

def update_infection_tree (messages : dict[int, list[tuple[int, int]]], infected : set[int], forest : list[Node], unixts : int):
    '''
    function that process the queue of messages: it choose a random message from the queue and
    if the message is infected, it will added to the infection tree
    input: messages is the queue of messages, infected is the set of infected nodes, forest is the forest of the infection
    output: it doesn't return anything, it just update the set of infected nodes and the forest of the infection
    '''

    for dst, data in messages.items():
        src, state = random.choice(data)
        if state == 1:
            new_node = Node(dst, unixts)
            add_infected_edges (new_node, forest, src)
            infected.add(dst)
    messages.clear()

def add_infected_edges (new_node : Node, forest : list[Node], src: int):
    ''''
    function that add a new infected edge between the dst node and each src node that has the selected id
    input: new_node is the node that has been infected, forest is the forest of the infection
    output: it doesn't return anything, it just update the forest of the infection
    '''
    for tree in forest:
        if tree.id == src and tree.timestamp < new_node.timestamp:
            tree.add_child(new_node)
        else:
            add_infected_edges (new_node, tree.children, src)

# ------------------------- choose nodes -------------------------

def count_subtree_size (forest: list[Node]):
    for tree in forest:
        count_subtree_size_rec(tree)

def count_subtree_size_rec (tree: Node):
    if tree.children == []:
        tree.subtree_size = 1
    else:
        for child in tree.children:
            count_subtree_size_rec(child)
            tree.subtree_size += child.subtree_size

def choose_nodes (forest: list[Node], seed_set: set[int], budget: int) -> set[int]:
    '''
    function that choose k nodes from the forest
    input: forest is the forest of the infection, seed_set is the set of initial infected nodes, k is the number of nodes to choose
    output: the set of nodes chosen
    '''

    # count the size of the subtree of each node
    count_subtree_size(forest)


    # choose k nodes from the nodes with the highest subtree size
    set_chosen_nodes = set()
    for _ in range(budget):
        chosen_node = -1
        max_subtree = 0
        for tree in forest:
            max_subtree, chosen_node = choose_nodes_rec(tree, seed_set, max_subtree, chosen_node, set_chosen_nodes)
        set_chosen_nodes.add(chosen_node)
    
    return set_chosen_nodes

def choose_nodes_rec (tree: Node, seed_set: set[int], max_subtree: int, node : int, set_chosen_nodes: set[int]):
    if tree.subtree_size > max_subtree and tree.id not in seed_set and tree.id not in set_chosen_nodes:
        max_subtree = tree.subtree_size
        node = tree.id
    for child in tree.children:
        max_subtree, node = choose_nodes_rec(child, seed_set, max_subtree, node, set_chosen_nodes)
    return max_subtree, node

def find_best_node (nodes : dict[int, int], budget : int) -> list[int]:

    # sort the nodes by their subtree size
    sorted_nodes = {k: v for k, v in sorted(nodes.items(), key=itemgetter(1), reverse=True)}
    return list(sorted_nodes.keys())[:budget]

# ------------------------- Random Algorithm -------------------------

def choose_random_nodes (budget : int, seed_set: set[int], nodes: set[int]):
    '''
    function that choose k nodes randomly
    input: budget is the number of nodes to choose
    output: the set of nodes chosen
    '''
    set_chosen_nodes = set()
    for _ in range(budget):
        chosen_node = random.choice(list(nodes))
        while chosen_node in seed_set or chosen_node in set_chosen_nodes:
            chosen_node = random.choice(list(nodes))
        set_chosen_nodes.add(chosen_node)
    return set_chosen_nodes

def count_nodes (src: int, dst: int, list_nodes: set[int]):
    list_nodes.add(src)
    list_nodes.add(dst)
    return list_nodes


# ------------------------- Main -------------------------

if __name__ == "__main__":
    
    filename = "CollegeMsg.txt"

    seed_set = {41, 9, 400, 321, 67, 289, 555, 266, 713, 642, 638, 42, 448, 986, 1000, 194, 12, 250, 105, 1113}
    node_budget = 100
    times = 100

    # set that contains all the nodes of the graph
    nodes = set()

    # dictionary that contains the number of times that each node has been removed from the forest in the subtree algorithm
    removed_nodes_subtree = defaultdict(int)

    first_simulation = simulate_infection (seed_set, filename, nodes=nodes)
    print(f"First simulation: {len(first_simulation)}")

    # simulation and selection of the nodes with the subtree algorithm
    for _ in range (times):
        forest = forward_forest (seed_set, filename)

        selected_node_subtree = choose_nodes (forest, seed_set, node_budget)
        for node in selected_node_subtree:
            removed_nodes_subtree[node] = removed_nodes_subtree[node] + 1

    selected_nodes_subtree = find_best_node (removed_nodes_subtree, node_budget)
    print(f"Selected nodes subtree: {selected_nodes_subtree}")

    average_subtree = 0
    for _ in range(times):
        second_simulation_subtree = simulate_infection (seed_set, filename, selected_nodes_subtree)
        average_subtree += len(second_simulation_subtree)
    print(f"Infected nodes subtree: {average_subtree/times}")

    # simulation and selection of the nodes with the random algorithm
    selected_node_random = choose_random_nodes (node_budget, seed_set, nodes)
    print(f"Selected nodes random: {selected_node_random}")
    
    average_random = 0
    for _ in range(times):
        second_simulation_random = simulate_infection (seed_set, filename, selected_node_random)
        average_random += len(second_simulation_random)
    print(f"Infected nodes random: {average_random/times}")