from hypothesis import given, assume
import hypothesis.strategies as st

from nose.tools import *

from flownetpy import FlowNetwork
from flownetpy.flowmodel import linear

import numpy as np
import networkx as nx


class TestCore:

    def setUp(self):
        self.K_stable = 10

        # setup a 2-node graph
        G = nx.Graph()
        G.add_edge(1, 2, weight=self.K_stable)
        inputs = {1: 1, 2: -1}
        self.two_node_net = FlowNetwork(G, inputs, linear, weight='weight')

        # setup a ring network with inputs -1 +1 -1 +1...
        self.ring_size = 8
        ring_graph = nx.cycle_graph(self.ring_size)
        for u, v in ring_graph.edges():
            ring_graph[u][v]['weight'] = self.K_stable
        inputs = {
            node: (node % 2 - 0.5) * 2 for node in np.arange(self.ring_size)}
        self.ring_net_even = FlowNetwork(
            ring_graph, inputs, linear, weight='weight')

        # setup a ring network with inputs +1 +1 +1 +1 -1 -1 -1 -1 ...
        inputs = {node: (int(node < self.ring_size / 2) - 0.5)
                  * 2 for node in np.arange(self.ring_size)}
        self.ring_net_odd = FlowNetwork(
            ring_graph, inputs, linear, weight='weight')

    # Test fixed points for simple networks
    @given(st.floats(min_value=0.0001, max_value=10))
    def test_2node_fixed_point(self, K):
        """Fixed point should be 1"""
        for u, v in self.two_node_net.edges():
            self.two_node_net[u][v]['weight'] = K

        fp_2node = self.two_node_net.steady_flows()
        assert_almost_equal(fp_2node[(1, 2)], 1, places=4)

    @given(st.floats(min_value=0.0001, max_value=10))
    def test_even_ring_fixed_point(self, K):
        """The flows should look like -0.5 0.5 -0.5 0.5..."""
        for u, v in self.ring_net_even.edges():
            self.ring_net_even[u][v]['weight'] = K

        fp_ring = self.ring_net_even.steady_flows()
        assert(np.allclose([flow - (u % 2 - 0.5)
                            for (u, v), flow in fp_ring.items()], 0, atol=1e-6))

    @given(st.floats(min_value=0.0001, max_value=10))
    def test_odd_ring_fixed_point(self, K):
        """The flows should look like 1 -1 1 -1 ..."""
        for u, v in self.ring_net_odd.edges():
            self.ring_net_odd[u][v]['weight'] = K

        nnodes = self.ring_net_odd.number_of_nodes()
        fp_ring = self.ring_net_odd.steady_flows()
        fp_ring_array = [fp_ring[(i, (i + 1) % nnodes)] for i in range(nnodes)]
        fp_exact_array = [-1, 0, 1, 2, 1, 0, -1, -2]

        assert(np.allclose(fp_ring_array, fp_exact_array, atol=1e-6))

