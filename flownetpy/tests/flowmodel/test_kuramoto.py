from hypothesis import given, assume
import hypothesis.strategies as st


from nose.tools import *

from flownetpy import FlowNetwork
from flownetpy.flowmodel import kuramoto

import numpy as np
import networkx as nx


class TestHelperfuncs:
    """ Test the helpedr functions"""
    @given(x=st.floats(min_value=-10000, max_value=10000))
    def test_mod_pi_range(self, x):
        assert(np.abs(kuramoto._mod_pi(x) < np.pi))

    @given(x=st.lists(st.floats(min_value=-10000, max_value=10000), min_size = 1, max_size = 100))
    def test_mod_pi_sanity(self, x):
        assert(np.all(np.abs(kuramoto._mod_pi(x) < np.pi)))

    @given(m=st.integers(min_value=-10000, max_value=10000))
    def test_mod_pi_even_pi(self, m):
        """_mod_pi(even_multiple_of_pi)==0"""
        assert_almost_equal(kuramoto._mod_pi(2 * m * np.pi), 0)

    @given(m=st.integers(min_value=-10000, max_value=10000))
    def test_mod_pi_odd_pi(self, m):
        """_mod_pi(odd_multiple_of_pi)==+/- 1"""
        assert_almost_equal(
            np.abs(kuramoto._mod_pi((2 * m + 1) * np.pi)), np.pi)

    @given(size=st.integers(min_value=3))
    def test_random_stableop_initguess(self, size):
        """this function should return angles with |successive difference| < pi/2 """
        arr = kuramoto._random_stableop_initguess(size)
        assert(
            (np.abs(kuramoto._mod_pi(arr - np.roll(arr, 1))) <= np.pi / 2).all())

    @given(delta=st.floats(min_value=-np.pi / 2, max_value=np.pi / 2), size=st.integers(min_value=4, max_value=100))
    def test_omega_equispaced(self, delta, size):
        """
        checks omega of a ring network  with equispaced thetas
        """
        assume(not np.allclose(((size - 1) * delta / np.pi - 1) % 2, 0))
        self.ring_net = nx.cycle_graph(size)
        nnodes = self.ring_net.number_of_nodes()
        thetas = np.arange(nnodes) * delta
        assert_almost_equal(kuramoto._omega(self.ring_net, [np.arange(size)], thetas)[0],
                            ((nnodes - 1) * delta + kuramoto._mod_pi((1 - nnodes) * delta)) / 2 / np.pi)


class TestCore:

    def setUp(self):
        self.K_stable = 10

        # setup a 2-node graph
        G = nx.Graph()
        G.add_edge(1, 2, weight=self.K_stable)
        inputs = {1: 1, 2: -1}
        self.two_node_net = FlowNetwork(G, inputs, kuramoto, weight='weight')

        # setup a ring network with inputs -1 +1 -1 +1...
        self.ring_size = 8
        ring_graph = nx.cycle_graph(self.ring_size)
        for u, v in ring_graph.edges():
            ring_graph[u][v]['weight'] = self.K_stable
        inputs = {
            node: (node % 2 - 0.5) * 2 for node in np.arange(self.ring_size)}
        self.ring_net_even = FlowNetwork(
            ring_graph, inputs, kuramoto, weight='weight')

        # setup a ring network with inputs +1 +1 +1 +1 -1 -1 -1 -1 ...
        inputs = {node: (int(node < self.ring_size / 2) - 0.5)
                  * 2 for node in np.arange(self.ring_size)}
        self.ring_net_odd = FlowNetwork(
            ring_graph, inputs, kuramoto, weight='weight')

    # Test fixed points for simple networks
    @given(st.floats(min_value=0.0001, max_value=0.1))
    def test_2node_fixed_point(self, dK):
        """Fixed point should be 1"""
        for u, v in self.two_node_net.edges():
            self.two_node_net[u][v]['weight'] = 1+dK

        fp_2node, data = self.two_node_net.steady_flows(
            initguess=np.array([0, 0]))
        assert_almost_equal(fp_2node[(1, 2)], 1, places=4)

    @given(st.floats(min_value=0.0001, max_value=0.1))
    def test_even_ring_fixed_point(self, dK):
        """The flows should look like -0.5 0.5 -0.5 0.5..."""
        for u, v in self.ring_net_even.edges():
            self.ring_net_even[u][v]['weight'] = 0.5 + dK

        fp_ring, data = self.ring_net_even.steady_flows(initguess=np.zeros(
            self.ring_net_even.number_of_nodes()))
        assert(np.allclose([flow - (u % 2 - 0.5)
                            for (u, v), flow in fp_ring.items()], 0, atol=1e-6))

    @given(st.floats(min_value=0.0001, max_value=0.1))
    def test_odd_ring_fixed_point(self, dK):
        """The flows should look like 1 -1 1 -1 ..."""
        for u, v in self.ring_net_odd.edges():
            self.ring_net_odd[u][v]['weight'] = self.ring_size/4 + dK

        nnodes = self.ring_net_odd.number_of_nodes()
        fp_ring, data = self.ring_net_odd.steady_flows(
            initguess=np.zeros(nnodes))
        fp_ring_array = [fp_ring[(i, (i + 1) % nnodes)] for i in range(nnodes)]
        fp_exact_array = [-1, 0, 1, 2, 1, 0, -1, -2]

        assert(np.allclose(fp_ring_array, fp_exact_array, atol=1e-6))

    # Test that no fixed point below critical coupling
    @given(st.floats(min_value=0.0001, max_value=0.1))
    def test_2node_unstable(self, dK):
        for u, v in self.two_node_net.edges():
            self.two_node_net[u][v]['weight'] = 1 - dK

        fp, data = self.two_node_net.steady_flows(
            initguess=np.array([0, 0]))
        assert_is_none(fp)

    @given(st.floats(min_value=0.0001, max_value=0.1))
    def test_even_ring_unstable(self, dK):
        for u, v in self.ring_net_even.edges():
            self.ring_net_even[u][v]['weight'] = 0.5 - dK

        fp, data = self.ring_net_even.steady_flows()
        assert_is_none(fp)

    @given(st.floats(min_value=0.0001, max_value=0.1))
    def test_odd_ring_unstable(self, dK):
        for u, v in self.ring_net_odd.edges():
            self.ring_net_odd[u][v]['weight'] = self.ring_size/4 - dK

        fp, data = self.ring_net_odd.steady_flows()
        assert_is_none(fp)

