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
import numpy as np


if __name__ == "__main__":
    
    filename = "fb-forum.txt"
    degrees_in = []
    degrees_out = []
    degrees = []

    attack_set_subree = [388, 389, 777, 538, 418, 424, 555, 431, 49, 434, 435, 51, 308, 185, 442, 187, 445, 447, 64, 65, 452, 205, 83, 90, 220, 735, 375, 98, 100, 741, 870, 871, 743, 361, 873, 231, 237, 493, 495, 239, 369, 498, 371, 244, 238, 759, 636, 253, 126, 767]
    attack_set_centrality = [93, 290, 592, 395, 388, 759, 734, 96, 9, 392, 39, 389, 538, 870, 62, 387, 437, 686, 3, 637, 240, 443, 703, 49, 742, 376, 362, 91, 83, 154, 274, 92, 445, 394, 18, 346, 90, 102, 869, 424, 50, 244, 435, 636, 363, 313, 222, 183, 383, 99]

    # find common nodes
    common_nodes = set(attack_set_subree).intersection(set(attack_set_centrality))
    print(f"Common nodes: {common_nodes}")
    print(f"Number of common nodes: {len(common_nodes)}")


    # read the file
    with open(filename, 'r') as f:
        for line in f:
            src, dst, unixts = line.split(",")
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


    # print centrality degrees
    for node in attack_set_centrality:
        print(f"Node {node} centrality degree: {degrees_in[node]} + {degrees_out[node]} = {degrees_in[node] + degrees_out[node]}")

    print("\n\n")
    for node in attack_set_subree:
        print(f"Node {node} subtree degree: {degrees_in[node]} + {degrees_out[node]} = {degrees_in[node] + degrees_out[node]}")

    # plot the degrees of nodes selected by subtree attack and centrality attack
    set_plot_subtree = list()
    set_plot_centrality = list()
    fig, ax = plt.subplots(figsize=(10, 5))

    # histogram of degrees of nodes selected by subtree attack
    for node in attack_set_subree:
        set_plot_subtree.append(degrees_in[node] + degrees_out[node])

    # histogram of degrees of nodes selected by centrality attack
    for node in attack_set_centrality:
        set_plot_centrality.append(degrees_in[node] + degrees_out[node])
    
    plt.hist([set_plot_centrality, set_plot_subtree], bins=100, alpha=0.5)
    plt.legend(['Centrality', 'Subtree'], loc='upper right', fontsize=15)


    ax.set_xlabel('Degree')
    ax.set_ylabel('Number of nodes')

    plt.show()