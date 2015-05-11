import numpy as np
import networkx as nx


#The linear Poiseullie flow in a network

def fixed_point(flownet):
    """
    The fixed points are given by:
        \sum_j (p_j-p_i)
    """
    L=np.array(nx.laplacian_matrix(flownet))
    I=np.array([flownet.node[n]['input'] for n in flownet.nodes()])

    pressures=np.insert(np.dot(np.linalg.inv(L[1:,1:]), I[1:]), 0, 0)

    node_indices={node:idx for idx,node in enumerate(flownet.nodes())}

    if flownet.weight_attr:
        flows={(u,v):(pressures[node_indices[u]]-pressures[node_indices[v]])*dat[flownet.weight_attr] for (u,v,dat) in flownet.edges()}
    else:
        flows={(u,v):pressures[node_indices[u]]-pressures[node_indices[v]] for (u,v) in flownet.edges()}
    return flows
