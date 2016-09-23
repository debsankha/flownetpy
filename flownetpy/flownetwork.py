"""
A module for flow network simulations
"""

from __future__ import division, print_function
import networkx as nx


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
        self.weight_attr = weight

        if isinstance(inputs, dict):
            # then inputs is a dictionary
            for node in inputs.keys():
                self.node[node]['input'] = inputs[node]
        else:
            # Assume inputs is a list-like object with
            # the same order as graph.nodes()
            for node, inpt in zip(graph.nodes(), inputs):
                self.node[node]['input'] = inputs[node]

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
