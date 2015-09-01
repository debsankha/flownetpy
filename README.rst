A python package to study flow networks
========================================
.. image:: https://travis-ci.org/debsankha/flownetpy.svg?branch=master
   :target: https://travis-ci.org/debsankha/flownetpy
   :alt: Testing status

.. image:: http://img.shields.io/pypi/v/flownetpy.svg
  :target: https://pypi.python.org/pypi/flownetpy
  :alt: PyPI version

.. image:: https://readthedocs.org/projects/flownetpy/?badge=latest
   :target: http://flownetpy.readthedocs.org/en/latest/
   :alt: Documentation Status

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
