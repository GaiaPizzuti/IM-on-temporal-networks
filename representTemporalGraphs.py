import random
import igraph as ig
from matplotlib import pyplot as plt

# ------------------- Plot function -------------------

def graph_visualization (filename : str):
    '''
    function that visualize the forest of the infection
    input: forest is the forest of the infection, filename is the name of the file containing the graph
    output: it doesn't return anything, it just create a graph visualization
    '''

    # create a graph
    G = ig.Graph.Read_Ncol(filename, names=True, directed=True)

    # create a list of colors for the nodes
    colors = ["red", "light blue", "green", "yellow", "orange", "purple", "pink", "grey"]

    fig, ax = plt.subplots(figsize=(5, 5))
    ig.plot(
        G,
        target=ax,
        vertex_size=0.2, # size of the nodes
        vertex_color=[random.choice(colors) for i in range(len(G.vs))],
        vertex_label=G.vs["name"],
        vertex_label_size=7.0,
        vertex_frame_width=4.0,
        vertex_frame_color="white",
        edge_width=0.5,
        edge_color=["grey"],
    )
    plt.show()

# ------------------- Main -------------------

if __name__ == "__main__":
    filename = "graph.txt"
    graph_visualization(filename)