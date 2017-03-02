"""
A module for flow network simulations
"""

from __future__ import division, print_function
import networkx as nx
from numbers import Number

class FlowNetwork(nx.Graph):
    """
    A class to describe a flow network. 

    A flow network is a graph with two properties:
        1.  Some amount of flow (called input) enters/leaves through its each node.
        2.  Each edge transports some flow (called current). 

    How the input flows distribute themselves into currents 
    is determined by a :class:`flowmodel`. 
    """

    def __init__(self, graph, inputs, weight=None):
        """
        Parameters
        ----------
        graph: networkx graph.
            DiGraphs and MultiGraphs not supported.
        input: dictionary.
            nodes as keys and inputs as values; e.g:
            {node_1: 1, node_2: -1, ...}
        flowmodel: class:`flowmodel` module.
        """
        nx.Graph.__init__(self, graph)
        if isinstance(weight, Number):
            # assign uniform weight to all edges
            for u,v in self.edges():
                self[u][v]['weight'] = weight
            self.weight_attr = 'weight'
        elif isinstance(weight, str):
            # assume graph aupplied already has specified weights
            # only point self.weight_attr to the correct attribute
            self.weight_attr = weight
        else:
            raise ValueError("We do not understand the meaning of weight %r"%weight)

        if isinstance(inputs, dict):
            # then inputs is a dictionary
            for node in inputs.keys():
                self.node[node]['input'] = inputs[node]
        else:
            # Assume inputs is a list-like object with
            # the same order as graph.nodes()
            for node, inpt in zip(graph.nodes(), inputs):
                self.node[node]['input'] = inpt

    def steady_flows(self, **kwargs):
        """
        Returns the steady state flows.

        Keyword Args
        ------------
            Whatever is required by the flows method of the flowmodel. 

        Returns
        -------
        F: dictionary
           A set of steady state flows in the network in form of a dictionary; s.t.
           F[(u,v)] == flow from u to v
        infodict: dictionary
           Additional conditions that lead to these flows. 

        Note
        ----
        Depending on the flowmodel, the returned flows may not be unique.
        """
        raise NotImplementedError
