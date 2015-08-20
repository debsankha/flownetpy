from hypothesis import given, assume
import hypothesis.strategies as st


from nose.tools import *

from flownetwork import FlowNetwork
from flowmodels import kuramoto

import numpy as np
import networkx as nx


class TestHelperfuncs:

    def setUp(self):
        ring_graph = nx.cycle_graph(8)
        inputs = {node: 1 for node in ring_graph.nodes()}
        self.ring_net = FlowNetwork(ring_graph, inputs, kuramoto)

    @given(x=st.floats(min_value=-10000, max_value=10000))
    def test_mod_pi(self, x):
        assert(np.abs(kuramoto._mod_pi(x) < np.pi))

    @given(size=st.integers(min_value=3))
    def test_random_stableop_initguess(self, size):
        arr = kuramoto._random_stableop_initguess(size)
        assert(
            (np.abs(kuramoto._mod_pi(arr - np.roll(arr, 1))) <= np.pi / 2).all())

    @given(delta=st.floats(min_value=-8 * np.pi / 2, max_value=8 * np.pi / 2))
    def test_omega(self, delta):
        nnodes = self.ring_net.number_of_nodes()
        thetas = np.arange(nnodes) * delta
        assert_almost_equal(kuramoto._omega(self.ring_net, thetas)[0],
                            ((nnodes - 1) * delta + kuramoto._mod_pi((1 - nnodes) * delta)) / 2 / np.pi)
