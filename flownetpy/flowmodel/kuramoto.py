from  __future__ import division

import numpy as np
import networkx as nx
from scipy.integrate import odeint

from .tools import FlowDict

TMAX = 600
TOL = 10e-6
NTRY=10

def steady_flows(flownet, initguess=None, extra_output=True):
    """
    Computes the steady state flows. 

    Args:
        flownet: A FlowNetwork object
        initguess: Initial conditions
        extra_output: boolean

    Returns:
        A dictionary
            d = {edge1 : flow1, edge2 : flow2,...}
        If extra_output=True, returns another dictionary
            data = {initguess: the_initial_condition, 'thetas': steady_state_thetas, 'omega': winding_vector}
    """

    thetas, initguess = _try_find_fps(NTRY, flownet, initguess=initguess)

    if thetas is None:
        return None, {'initguess': initguess}

    node_indices = {node: idx for idx, node in enumerate(flownet.nodes())}
    flows = FlowDict({(u, v): np.sin(thetas[node_indices[u]] - thetas[node_indices[v]])*
        dat.get(flownet.weight_attr, 1) for (u, v, dat) in flownet.edges(data=True)})

    if extra_output:
        omega = _omega(flownet, nx.cycle_basis(flownet), thetas)
        return flows, {'initguess': initguess, 'thetas': thetas, 'omega': omega}
    else:
        return flows

def _try_find_fps(ntry, flownet, tmax=TMAX, tol=TOL, initguess=None):
    """
    Tries to find a fixed point of the Kuramoto network. 

    Args:
        ntry    : number of initial conditions that will be tried to reach a fixed point
        flownet : a FlowNetwork  object
        tmax    : integration time
        tol     : the odesolver ends when the variance of thetas  are less than tol
        initguess : initial condition. If specified, ntry doesn't have any effect

    Returns:
        (fixed point, initguess)

    Note:
        If no fixed point is found, returns (None, initguess)
    """

    dt = tmax / 1000

    if initguess is not None: # then use the specified initguess    
        sol = _evolve(flownet, np.arange(0, tmax, dt), initguess = initguess)
        if _has_converged(sol):
            return sol[-1], initguess
        else:
            return None, initguess
    
    for ntry in range(ntry): # otherwise try `ntry` random initguesses
        initguess = _random_stableop_initguess(flownet.number_of_nodes())
        sol = _evolve(flownet, np.arange(0, tmax, dt), initguess)
        if _has_converged(sol):
            return sol[-1], initguess

    return None, initguess


def _evolve(flownet, tarr, initguess=None):
    """
    Evolves the flow network from `initguess` by timesteps in `tarr`
    """
    M = nx.incidence_matrix(flownet, oriented=True).toarray()
    Mw = nx.incidence_matrix(flownet, oriented=True, weight=flownet.weight_attr).toarray()
    P = np.array([flownet.node[n]['input'] for n in flownet.nodes()])
    
    if initguess is None:
        initguess = _random_stableop_initguess(flownet.number_of_nodes())
    
    return odeint(_kuramoto_ode, initguess, t=tarr, args=(M, Mw, P))


def _has_converged(time_series, window_size=0):
    """
    Detects if the time series has converged, by
    checking the values during the window given by 'window_size'
    """

    if window_size == 0:  # The window over which time series must be constant
        window_size = time_series.shape[0]//10 

    return np.allclose(np.var(time_series[-window_size:, :], axis=0), 0)


def _kuramoto_ode(th, t, M_I, M_I_w, P):
    """
    Args:
	    th: theta, array with size=nnodes
	    t: time
	    M_I: unweighted oriented incidence matrix
	    M_I_W: weighted oriented incidence matrix
	    P: Power production at each node
    """
    return P - np.dot(M_I_w, np.sin(np.dot(M_I.T, th)))



def _omega(graph, cycles, thetas):
    """
    Calculates the winding number:
        (\sum_{i,j \in cycle} asin(\theta_j-\theta_i))/2\pi
    """
    omegas = []
    node2idx = {node:idx for idx, node in enumerate(graph.nodes())}
    for cycle in cycles:
        omega = 0
        angles_cycle = np.array([thetas[node2idx[node]]\
                       for node in cycle])
        phasediffs_cycle = _mod_pi(angles_cycle - np.roll(angles_cycle, 1))


        omega = np.sum(phasediffs_cycle) / np.pi / 2
        omegas.append(omega)
    return omegas


def _random_stableop_initguess(size):
    """
    Args:
        size: int

    Returns:
        An array res of random numbers s.t. 
        |res[i]-res[i+1 % size]| < \pi/2
    """
    low = -np.pi / 2
    high = np.pi / 2
    
    initguess = np.cumsum(np.random.uniform(low=low, high=high, size=size - 1))
    initguess = np.insert(initguess, 0, 0)

    if np.abs(_mod_pi(initguess[-1])) > np.pi/2:
        return _random_stableop_initguess(size)
    else:
        return initguess


def _mod_pi(angle):
    """
    given an angle, returns an equivalent angle
    within the interval [-pi,pi]

    Warning:
        Result is not well defined for angle = pi*(2k+1)
    """
    rem = np.remainder(angle, 2 * np.pi)
    return np.where(rem<=np.pi, rem, rem-2*np.pi)


def projector_rotating(size):
    X=np.diag(np.arange(1, size), k=-1)[:,:-1]
    X[np.triu_indices_from(X,k=0)]=-1
    
    colnorms=np.linalg.norm(X, axis=0)
    
    return X/colnorms[np.newaxis, :]  #Normalize

def contract_map(thetas, G, inputs, K):
    V=projector_rotating(thetas.shape[0]+1)
    B=nx.incidence_matrix(G, weight=None, oriented=True).toarray()
    
    bTv=np.dot(B.T, V)
    
    W=np.diag(np.sinc(np.dot(bTv, thetas)))
    
    op = np.dot(bTv.T, np.dot(W, bTv))
    om_bar=np.dot(V.T, inputs)
    return np.linalg.solve(op*K, om_bar)


def fp_by_map(flownet, K, initguess = None):
    P = np.array([flownet.node[node]['input'] for node in flownet.nodes()])
    V = projector_rotating(flownet.number_of_nodes())

    if initguess is None:
        initguess = np.random.random(flownet.number_of_nodes())

    thetas = np.dot(V.T, initguess)

    maxstep = 500
    tol = 10e-4

    diff = tol+1
    nstep = 0

    while nstep < maxstep and diff > tol:
        newthetas = contract_map(thetas, flownet, P, K)
        diff = np.linalg.norm(newthetas - thetas)
        thetas = newthetas
        nstep += 1


    return np.dot(V, thetas)

   

