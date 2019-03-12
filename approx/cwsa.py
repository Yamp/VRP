import operator

import numpy as np
import pandas as pd


# Clarke-Wright Savings Algorithm
class CWSA(object):
    """
    argument:
    create an object with 'distances' attributes.
    self.distances[(from_node,to_node)] = distance
    output:
    """

    def __init__(self):
        self.distances = {}

    def add_dist(self, from_node, to_node, distance):
        if from_node != 'DC' and to_node != 'DC':
            nodes = tuple(sorted((from_node, to_node)))
            self.distances[nodes] = distance
        elif from_node == 'DC':
            self.distances[(to_node, from_node)] = distance
        elif to_node == 'DC':
            self.distances[(from_node, to_node)] = distance

    def dist_matrix(self):
        """
        argument: cwsa object

        output:
        matr (numpy array): rows = from_node
                                columns = to_node
                                entries = distance (above diagonal element)
                                          diagonal and below diagonal elements are 0
        """
        from_list = []
        dist_dict = self.distances
        for from_node, to_node in dist_dict:
            if from_node not in from_list:
                from_list.append(from_node)
        from_list.sort()
        matr = np.zeros((len(from_list), len(from_list) + 1))

        for from_node, to_node in dist_dict:
            if to_node != 'DC':
                matr[from_node - 1, to_node - 1] = dist_dict[(from_node, to_node)]
            else:
                matr[from_node - 1, -1] = dist_dict[(from_node, to_node)]
        return matr


    def CWSA_savings(self):
        """
        Given cwsa object, provide savings and distance table of
        argument:
        (object): cwsa object with complete distances attribute added by add_dist
                  function
        output:
        savings_dict(dataframe): 1st column   = index
                              2nd column   = (from_node,to_node)
                              3rd column   = distance/cost saving for these nodes
        matr (dataframe): distance/cost (above diagonal element) and
                              saving (below diagonal element) of each pair of nodes
        """
        matr = self.dist_matrix()
        savings_dict = {}

        for i in range(np.shape(matr)[0]):
            for j in range(i + 1, np.shape(matr)[0]):
                saving = matr[i, -1] + matr[j, -1] - matr[i, j]
                matr[j, i] = saving
                savings_dict[(i + 1, j + 1)] = saving

        CWSA_list = sorted(savings_dict.items(), key=operator.itemgetter(1), reverse=True)
        CWSA_savings_df = pd.DataFrame(CWSA_list)
        CWSA_df = pd.DataFrame(matr)
        return CWSA_df, CWSA_savings_df
