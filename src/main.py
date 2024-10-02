from copy import deepcopy
import sys
from temporalGraph import influence_maximization, spread_infection
from subTreeInfection import subtrees_methods
from vsCentrality import centrality_analysis
from comparison import result_comparison
from degreeNodes import degree_nodes
from cc import compare_cc

filename = sys.argv[1]
node_budget = int(sys.argv[2])

def adversarial_attack_at_influence_maximization ():
    '''
    main function
    
    it is needed to call this function with:
        - argv[1]: the name of the relative file's path containing the graph to analyze (e.g. data/email.txt)
    '''
    
    prob_of_being_infected = 0.2
    
    print('---- find seed set ----\n\n')
    
    seed_set = influence_maximization(filename, prob_of_being_infected)
    print('seed set:', seed_set)
    
    
    print('\n\n---- simulate infection ----\n\n')
    test_seed_set = deepcopy(seed_set)
    infected = spread_infection(test_seed_set, filename, prob_of_being_infected)
    print('number of infected nodes in the simulation:', infected)
    
    print('\n\n---- minimize infection with subtrees ----\n\n')
    
    subtree = subtrees_methods(filename, set(seed_set), node_budget, prob_of_being_infected)
    
    print('\n\n---- minimize infection with centrality ----\n\n')
    
    centrality = centrality_analysis(filename, set(seed_set), node_budget, set(subtree), prob_of_being_infected)
    
    print('\n\n---- result comparison ----\n\n')
    
    result_comparison(filename, set(seed_set), node_budget, set(subtree), set(centrality), prob_of_being_infected)
    
    degree_nodes(filename, subtree, centrality)
    
    compare_cc(filename, subtree, centrality)

if __name__ == '__main__':
    adversarial_attack_at_influence_maximization()