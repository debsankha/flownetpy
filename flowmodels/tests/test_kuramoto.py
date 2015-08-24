from hypothesis import given, assume
import hypothesis.strategies as st


from nose.tools import *

from flownetwork import FlowNetwork
from flowmodels import kuramoto

import numpy as np
import networkx as nx


class TestHelperfuncs:

    
    @given(x=st.floats(min_value=-10000, max_value=10000))
    def test_mod_pi_sanity(self, x):
        assert(np.abs(kuramoto._mod_pi(x) < np.pi))

    @given(m=st.integers(min_value=-10000, max_value=10000))
    def test_mod_pi_even_pi(self, m):
        """_mod_pi(even_multiple_of_pi)==0"""
        assert_almost_equal(kuramoto._mod_pi(2*m*np.pi) , 0)

    @given(m=st.integers(min_value=-10000, max_value=10000))
    def test_mod_pi_odd_pi(self, m):
        """_mod_pi(odd_multiple_of_pi)==+/- 1"""
        assert_almost_equal(np.abs(kuramoto._mod_pi((2*m + 1)*np.pi)) , np.pi)

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
        assume(not np.allclose(((size-1)*delta/np.pi - 1)%2, 0))
        self.ring_net = nx.cycle_graph(size)
        nnodes = self.ring_net.number_of_nodes()
        thetas = np.arange(nnodes) * delta
        assert_almost_equal(kuramoto._omega(self.ring_net, [np.arange(size)], thetas)[0],
                            ((nnodes - 1) * delta + kuramoto._mod_pi((1 - nnodes) * delta)) / 2 / np.pi)


class TestCore:

    def setUp(self):
        # setup a 2-node graph
        G=nx.Graph()
        G.add_edge(1, 2, weight = 10)
        inputs= {1:1, 2:-1}
        self.two_node_net = FlowNetwork(G, inputs, kuramoto)
        
        # setup a ring network with inputs -1 +1 -1 +1...
        ring_graph = nx.cycle_graph(8)
        for u,v in ring_graph.edges():
            ring_graph[u][v]['weight'] = 10
        inputs = {node: (node%2 - 0.5)*2 for node in np.arange(8)}
        self.ring_net_even = FlowNetwork(ring_graph, inputs, kuramoto)
        
        # setup a ring network with inputs -1 +1 -1 +1...
        inputs = {node: (int(node<4) - 0.5)*2 for node in np.arange(8)}
        print(inputs)
        self.ring_net_odd = FlowNetwork(ring_graph, inputs, kuramoto)

    def test_2node_fixed_point(self):
        fp_2node, data = self.two_node_net.fixed_point(initguess=np.array([0, 0]))
        assert_almost_equal(fp_2node[(1,2)], 1, places = 4)


    def test_even_ring_fixed_point(self):
        """The flows should look like -0.5 0.5 -0.5 0.5..."""
        fp_ring, data = self.ring_net_even.fixed_point(initguess=np.zeros(
                 self.ring_net_even.number_of_nodes()))
        assert(np.allclose([flow - (u%2-0.5) for (u,v), flow in fp_ring.items()], 0))

    def test_odd_ring_fixed_point(self):
        """The flows should look like 1 1 1 ..."""
        nnodes = self.ring_net_odd.number_of_nodes()
        fp_ring, data = self.ring_net_odd.fixed_point(initguess=
                                                np.zeros(nnodes))
        print(fp_ring)
        fp_ring_array = [fp_ring[(i, i+1)] for i in range(nnodes-1)]
        fp_ring_array.append(fp_ring[0, nnodes-1])
        print(fp_ring_array)
        fp_exact_array = [-1, 0, 1, 2, 1, 0, 1, 2]

        assert(np.allclose(fp_ring_array, fp_exact_array))
        assert(np.allclose([flow - (u%2-0.5) for (u,v), flow in fp_ring.items()], 0))

