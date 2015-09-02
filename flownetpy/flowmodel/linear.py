import numpy as np
import networkx as nx

from .tools import FlowDict

# The linear Poiseullie flow in a network

def steady_flows(flownet):
    """
    The fixed points are given by:
        \sum_j (p_j-p_i)
    """
    L = nx.laplacian_matrix(flownet).toarray()
    I = np.array([flownet.node[n]['input'] for n in flownet.nodes()])

    pressures = np.insert(np.linalg.solve(L[1:, 1:], I[1:]), 0, 0)
    node_indices = {node: idx for idx, node in enumerate(flownet.nodes())}
    flows = FlowDict({(u, v): (pressures[node_indices[u]] - pressures[node_indices[v]]) * dat.get(
        flownet.weight_attr, 1) for (u, v, dat) in flownet.edges(data=True)})
    return flows
