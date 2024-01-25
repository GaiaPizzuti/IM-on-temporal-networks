from copy import deepcopy
import sys
from temporalGraph import influence_maximization, spread_infection
from subTreeInfection import minimize_infection
from vsCentrality import centrality_analysis

filename = sys.argv[1]

def adversarial_attack_at_influence_maximization ():
    '''
    main function
    
    it is needed to call this function with:
        - argv[1]: the name of the relative file's path containing the graph to analyze (e.g. data/email.txt)
    '''
    
    prob_of_being_infected = 0.2
    node_budget = 10
    
    print('---- find seed set ----\n\n')
    
    seed_set = influence_maximization(filename, prob_of_being_infected)
    print('seed set:', seed_set)
    
    
    print('\n\n---- simulate infection ----\n\n')
    test_seed_set = deepcopy(seed_set)
    infected = spread_infection(test_seed_set, filename, prob_of_being_infected)
    print('number of infected nodes in the simulation:', infected)
    
    print('\n\n---- minimize infection with subtrees ----\n\n')
    
    minimize_infection(filename, set(seed_set), node_budget, prob_of_being_infected)
    
    print('\n\n---- minimize infection with centrality ----\n\n')
    
    centrality_analysis(filename, set(seed_set), node_budget, prob_of_being_infected)

if __name__ == '__main__':
    adversarial_attack_at_influence_maximization()