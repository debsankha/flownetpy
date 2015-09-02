import hypothesis.strategies as st
from hypothesis import given
import numpy as np

from flownetpy.flowmodel.tools import FlowDict

_MAX=10000
_MIN=-10000


class TestFlowDict:
    @given(st.dictionaries(keys=st.frozensets(st.integers(min_value=_MIN, max_value=_MAX), min_size=2, max_size=2), values=st.floats(min_value=_MIN, max_value=_MAX)))
    def test_sanity(self, data):
        """
        tests that FlowDict[(v ,u)] = -FlowDict[(u, v)]
        """
        x=FlowDict({(u,v):val for (u,v), val in data.items()})
        assert(np.allclose([x[(u,v)] - x[(u,v)] for u,v in data.keys()],
              0))
        assert(np.allclose([x[(v,u)] + x[(u,v)] for u,v in data.keys()],
              0))
    
