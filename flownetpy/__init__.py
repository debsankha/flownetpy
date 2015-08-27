from __future__ import division, print_function
import networkx as nx
__all__ = ['FlowNetwork']


class FlowNetwork(nx.Graph):

    def __init__(self, graph, input, flowmodel, weight=None):
        """
        Creates a flow network with network topology given by `graph` and the input at each node given by `input`

        Arguments:
            `graph`: Any valid networkx graph
            `input`: A dictionary with nodes of `graph` as keys"""

        nx.Graph.__init__(self, graph)

        self.flowmodel = flowmodel
        self.weight_attr = weight
        for node in input.keys():
            self.node[node]['input'] = input[node]
       
    def fixed_point(self, **kwargs):
        """
        Returns a set of steady state flows in the network, in form of a dictionary, with each edge as a key. With additional parameters that lead to this fixed point, as well. 
        res[(u,v)]==flow from u to v
        """
        return self.flowmodel.fixed_point(self, **kwargs)
