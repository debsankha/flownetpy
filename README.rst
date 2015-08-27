A python package to study flow networks
========================================
This package contains tools to simulate a flow
according to user-definable flowmodels (e.g. linear Poiseuillie flow)
on any graph.


Usage
=====
>>> from flownetpy import FlowNetwork
>>> from flownetpy.flowmodels import linear
>>>
>>> C=nx.cycle_graph(4)
>>> I=np.array([1,-1,1,-1])
>>> KK=FlowNetwork(C,I,linear)
>>> 
>>> KK.fixed_point()
{(0, 1): 0.49999999999999994,
(0, 3): 0.49999999999999956,
(1, 2): -0.5000000000000006,
(2, 3): 0.5000000000000001}
