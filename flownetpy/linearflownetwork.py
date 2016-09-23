from  __future__ import division

from .flownetwork import FlowNetwork
from .tools import FlowDict

import numpy as np
import networkx as nx

TMAX = 200
TOL = 10e-6
NTRY=10

class LinearFlowNetwork(FlowNetwork):
    # The linear Poiseullie flow in a network
    def steady_flows(self):
        """
        The fixed points are given by:
            \sum_j (p_j-p_i)
        """
        L = nx.laplacian_matrix(self).toarray()
        I = np.array([self.node[n]['input'] for n in self.nodes()])

        pressures = np.insert(np.linalg.solve(L[1:, 1:], I[1:]), 0, 0)
        node_indices = {node: idx for idx, node in enumerate(self.nodes())}
        flows = FlowDict({(u, v): (pressures[node_indices[u]] - pressures[node_indices[v]]) * dat.get(
            self.weight_attr, 1) for (u, v, dat) in self.edges(data=True)})
        return flows
