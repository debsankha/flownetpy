Flow networks: some definitions
-------------------------------

**Flow network:** A flow network is an *undirected graph* through whose vertices certain
*input* currents are injected, and those currents are distrbuted through the
edges in the form of *flows* according to a *flow model*. 

**Definition:**
Let a flow network be defined as a tuple :math:`(G, \vec{I}, f)`, where :

-  :math:`G` is a graph with vertex set :math:`V` and edge set :math:`E`. 
-  :math:`I \in R^{|V|}` is a vector specifying **input currents** at each vertex :math:`v \in V`
-  :math:`f` is a *flow model* specifying flows :math:`F_{uv}` from node :math:`v` to node :math:`u`
 across each edge :math:`(u,v)\in E`:

.. math::
    f: E \to R^{|E|}

    f: (u,v) \mapsto F_{uv}

The flows must obey:

A.  the *continuity equation* at each node:

.. math::
    \sum_{(u,v)\in E}  I_u + F_{uv}  = 0

B.  the *reflexivity of flows* across each edge:

.. math::
    F_{uv} = -F_{vu}

