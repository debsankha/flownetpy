from hypothesis import given, assume
import hypothesis.strategies as st


from nose.tools import *

from flownetwork import FlowNetwork
from flowmodels import kuramoto

import numpy as np

class TestHelperfuncs:
    
    @given(x = st.floats(min_value=-10000, max_value=10000))
    def test_mod_pi(self, x):
        assert(np.abs(kuramoto._mod_pi(x)<np.pi))

if __name__=='__main__':
    x=TestHelperfuncs()

