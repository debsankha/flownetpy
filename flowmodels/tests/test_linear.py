from hypothesis import given, assume
import hypothesis.strategies as st


from nose.tools import *

from flownetwork import FlowNetwork
from flowmodels import linear

import numpy as np
import networkx as nx


class TestFixedpoint:
    
    def setUp(self):
        ring_graph = nx.cycle_graph(8)
        inputs = {node: 1 for node in ring_graph.nodes()}
        self.ring_net = FlowNetwork(ring_graph, inputs, linear)

