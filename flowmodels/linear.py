import numpy as np
import networkx as nx


# The linear Poiseullie flow in a network

def fixed_point(flownet):
    """
    The fixed points are given by:
        \sum_j (p_j-p_i)
    """
    L = np.array(nx.laplacian_matrix(flownet))
    I = np.array([flownet.node[n]['input'] for n in flownet.nodes()])

    pressures = np.insert(np.dot(np.linalg.inv(L[1:, 1:]), I[1:]), 0, 0)

    node_indices = {node: idx for idx, node in enumerate(flownet.nodes())}

    flows = {(u, v): (pressures[node_indices[u]] - pressures[node_indices[v]]) * dat.get(
        flownet.weight_attr, 1) for (u, v, dat) in flownet.edges(data=True)}
    return flows
