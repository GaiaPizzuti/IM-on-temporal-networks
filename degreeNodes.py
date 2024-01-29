# Description: This program reads a file with the following format:
# src dst unixts
# src: id of the source node
# dst: id of the target node
# unixts: unix timestamp of the edge
#
# The program will print the in and out degrees of each node
#

# ------------------------- Main -------------------------

from matplotlib import pyplot as plt

def degree_nodes (filename: str, attack_set_subtree: list, attack_set_centrality: list):
    '''
    function that check the degree of nodes selected by the subtree algorithm and by the centrality algorithm and plot the comparison
    and then print the number of edges removed by each algorithm
    
    input:
        - filename: str, the name of the file containing the information about the network
        - attack_set_subtree: list, list of nodes selected by the subtree algorithm
        - attack_set_centrality: list, list of nodes selected by the centrality algorithm
        
    output: None
    '''
    degrees_in = []
    degrees_out = []
    
    # find common nodes
    common_nodes = set(attack_set_subtree).intersection(set(attack_set_centrality))
    print(f"Common nodes: {common_nodes}")
    print(f"Number of common nodes: {len(common_nodes)}")


    # read the file
    with open(filename, 'r') as f:
        split_char = ' '
        if filename == 'data/fb-forum.txt':
            split_char = ','
        for line in f:
            src, dst, unixts = line.split(split_char)
            src, dst, unixts = int(src), int(dst), int(unixts)

            # if the src is not in the list, add 1 in the list in position src
            if len(degrees_in) <= src:
                for _ in range(src - len(degrees_in) + 1):
                    degrees_in.append(0)
            degrees_in[src] += 1

            # if the dst is not in the list, add 1 in the list in position dst
            if len(degrees_out) <= dst:
                for _ in range(dst - len(degrees_out) + 1):
                    degrees_out.append(0)
            degrees_out[dst] += 1

    # plot the degrees of nodes selected by subtree attack and centrality attack
    set_plot_subtree = list()
    set_plot_centrality = list()
    _, ax = plt.subplots(figsize=(10, 5))

    subtree_count = 0
    # histogram of degrees of nodes selected by subtree attack
    for node in attack_set_subtree:
        total_nodes = degrees_in[node] + degrees_out[node]
        set_plot_subtree.append(total_nodes)
        subtree_count += total_nodes

    centrality_count = 0
    # histogram of degrees of nodes selected by centrality attack
    for node in attack_set_centrality:
        total_nodes = degrees_in[node] + degrees_out[node]
        set_plot_centrality.append(total_nodes)
        centrality_count += total_nodes
    
    plt.hist([set_plot_centrality, set_plot_subtree], bins=100, alpha=0.5)
    plt.legend(['Centrality', 'Subtree'], loc='upper right', fontsize=15)
    
    print('Number of edges removed by subtrees algorithm: ', subtree_count)
    print('Number of nodes removed by centrality algorithm: ', centrality_count)

    ax.set_xlabel('Degree')
    ax.set_ylabel('Number of nodes')

    plt.show()


if __name__ == "__main__":
    
    filename = "data/email.txt"
    
    attack_set_subtree = [43, 88, 54, 25, 66, 80, 23, 48, 16, 35]
    attack_set_centrality = [54, 60, 71, 49, 25, 24, 48, 0, 26, 35]

    degree_nodes(filename, attack_set_subtree, attack_set_centrality)