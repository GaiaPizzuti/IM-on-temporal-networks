# ------------------------- class Node -------------------------

from collections import defaultdict
import random
import igraph as ig
from matplotlib import patches
from matplotlib.axes import Axes
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

def simulate_infection(seed_set : set, filename : str, removed_nodes=[]):
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

def choose_nodes (forest: list[Node], seed_set: set[int]) -> int:
    '''
    function that choose k nodes from the forest
    input: forest is the forest of the infection, seed_set is the set of initial infected nodes, k is the number of nodes to choose
    output: the set of nodes chosen
    '''

    # count the size of the subtree of each node
    count_subtree_size(forest)


    # choose k nodes from the nodes with the highest subtree size
    chosen_node = -1
    max_subtree = 0
    chosen_node = -1
    for tree in forest:
        chosen_node = choose_nodes_rec(tree, seed_set, max_subtree, chosen_node)
    
    return chosen_node

def choose_nodes_rec (tree: Node, seed_set: set[int], max_subtree: int, node : int) -> int:
    if tree.subtree_size > max_subtree and tree.id not in seed_set:
        max_subtree = tree.subtree_size
        node = tree.id
    for child in tree.children:
        node = choose_nodes_rec(child, seed_set, max_subtree, node)
    return node

def find_best_node (nodes : dict[int, int], budget : int) -> list[int]:

    # sort the nodes by their subtree size
    sorted_nodes = {k: v for k, v in sorted(nodes.items(), key=itemgetter(1), reverse=True)}
    return list(sorted_nodes.keys())[:budget]


# ------------------------- forest visualization -------------------------

def forest_visualization (infected: set[int], filename : str, fig : Figure, ax, removed_nodes=()):
    '''
    function that visualize the forest of the infection
    input: forest is the forest of the infection, filename is the name of the file containing the graph
    output: it doesn't return anything, it just create a graph visualization
    '''

    # create a graph
    G = ig.Graph.Read_Ncol(filename, names=True, directed=True)

    translated_removed_nodes = translate_nodes (G.vs, removed_nodes)

    # create the visualization
    infected_patch = patches.Patch(color='red', label='Infected')
    noninfected_patch = patches.Patch(color='grey', label='Non infected')
    fig.legend(handles=[infected_patch, noninfected_patch], loc='outside upper right')
    ig.plot(
        G,
        target=ax,
        vertex_size=0.2, # size of the nodes
        vertex_color=["grey" if int(node) not in infected else "red" for node in G.vs["name"]],
        vertex_label=G.vs["name"],
        vertex_label_size=7.0,
        vertex_frame_width=4.0,
        vertex_frame_color="white",
        edge_label=G.es["weight"],
        edge_label_size=7.0,
        edge_width=0.5,
        edge_color=["grey" if int(edge.source) not in translated_removed_nodes and int(edge.target) not in translated_removed_nodes else "white" for edge in G.es],
        edge_label_color=["black" if int(edge.source) not in translated_removed_nodes and int(edge.target) not in translated_removed_nodes else "white" for edge in G.es],
    )

def translate_nodes (vertices, removed_nodes) -> set[int]:
    translated_nodes = set()
    for vertex in vertices:
        if int(vertex["name"]) in removed_nodes:
            translated_nodes.add(vertex.index)
    return translated_nodes

# ------------------------- Main -------------------------

if __name__ == "__main__":
    
    filename = "graph.txt"

    seed_set = {0}
    node_budget = 1
    times = 100
    removed_nodes = defaultdict(int)
    
    fig, ax = plt.subplots(1, 3, figsize=(15, 15))
    ax0, ax1, ax2 = ax.flatten()

    forest_visualization (seed_set, filename, fig, ax0)

    first_simulation = simulate_infection (seed_set, filename)

    print(f"Infected nodes: {first_simulation}")
    
    forest_visualization (first_simulation, filename, fig, ax1)

    for _ in range (times):
        forest = forward_forest (seed_set, filename)

        selected_node = choose_nodes (forest, seed_set)
        removed_nodes[selected_node] = removed_nodes[selected_node] + 1

    selected_nodes = find_best_node (removed_nodes, node_budget)
    print(f"Selected nodes: {selected_nodes}")

    second_simulation = simulate_infection (seed_set, filename, selected_nodes)
    print(f"Infected nodes: {second_simulation}")

    forest_visualization (second_simulation, filename, fig, ax2, selected_nodes)

    ratio = len(second_simulation) / len(first_simulation)
    print(f"Ratio: {ratio}")

    plt.show()