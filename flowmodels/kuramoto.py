from  __future__ import division

import numpy as np
import networkx as nx
from math import sin, asin, pi
from scipy.integrate import ode

TMAX = 500
NTRY=10

def odeint(func, x0, t=None, args=None):
    """
    Integrate an ode for time array t
    """
    r = ode(func).set_integrator('vode', method='bdf')
    r.set_initial_value(x0, t[0]).set_f_params(*args)

    res = np.zeros((t.size, x0.size))
    res[0,:] = x0

    for idx, tnow in enumerate(t[1:]):
        r.integrate(tnow)
        res[idx+1, :] = r.y
    return res


def _kuramoto_ode(t, th, M_I, M_I_w, P):
    """
    th: theta, array with size=nnodes
    t: time
    M_I: unweighted oriented incidence matrix
    M_I_W: weighted oriented incidence matrix
    P: Power production at each node
    """
    return P - np.dot(M_I_w, np.sin(np.dot(M_I.T, th)))


def _has_converged(time_series, window_size=0):
    """
    detects if the time series has converged
    """

    if window_size == 0:  # The window over which time series must be constant
        window_size = time_series.shape[0]//10 

    return np.allclose(np.var(time_series[-window_size:, :], axis=0), 0)


def _try_find_fps(ntry, M, Mw, P, tmax=TMAX, tol=10e-4, initguess=None):
    """
    ntry: number of initial conditions that will be tried to reach a fixed point
    tol: the odesolver ends when the variance of thetas  are less than tol
    """

    assert(M.shape[0] == P.shape[0])  # The way it's supposed to be done...

    size = P.shape[0]
    dt = tmax / 1000

    if initguess is not None:
        sol = odeint(
            _kuramoto_ode, initguess, t=np.arange(0, tmax, dt), args=(M, Mw, P))

        if _has_converged(sol):
            return sol[-1], initguess
        else:
            return None, initguess

    for ntry in range(ntry):
        initguess = random_stableop_initguess(size)

        sol = odeint(
            _kuramoto_ode, initguess, t=np.arange(0, tmax, dt), args=(M, Mw, P))

        if _has_converged(sol):
            return sol[-1], initguess

    return None, initguess


def _omega(flownet, flows):
    """
    Calculates the winding number:
        (\sum_{i,j \in cycle} asin(\theta_j-\theta_i))/2\pi
    """
    omegas = []
    for cycle in nx.cycle_basis(flownet):
        omega = 0
        nnodes = len(cycle)
        for idx in range(nnodes):
            (u, v) = (cycle[idx], cycle[(idx + 1) % nnodes])
            try:
                omega += asin(flows[(u, v)] / flownet[u][v]['weight'])
            except KeyError:
                omega -= asin(flows[(v, u)] / flownet[u][v]['weight'])
        omega = int(omega / pi / 2)
        omegas.append(omega)
    return omegas


def random_stableop_initguess(size):
    """
    generate initial condition with phase differences <pi/2
    """
    low = -np.pi / 2
    high = np.pi / 2

    initguess = np.cumsum(np.random.uniform(low=low, high=high, size=size - 2))
    initguess = np.insert(initguess, 0, 0)

    lastangle = np.fmod(initguess[-1], 2 * np.pi)
    if lastangle > np.pi:
        lastangle = lastangle / 2 - np.pi
    else:
        lastangle = lastangle / 2

    return np.append(initguess, lastangle)


def mod_piby2(angle):
    rem = angle % (2 * np.pi)

    if rem < np.pi:
        return rem
    else:
        return rem - 2 * np.pi


def fixed_point(flownet, initguess=None, extra_output=True):
    M = nx.incidence_matrix(flownet, oriented=True).toarray()
    Mw = nx.incidence_matrix(flownet, oriented=True, weight=flownet.weight_attr).toarray()

    P = np.array([flownet.node[n]['input'] for n in flownet.nodes()])

    thetas, initguess = _try_find_fps(NTRY, M, Mw, P, initguess=initguess)

    if thetas is None:
        return None, {'initguess': initguess}

    node_indices = {node: idx for idx, node in enumerate(flownet.nodes())}

    if flownet.weight_attr:
        flows = {(u, v): sin(thetas[node_indices[u]] - thetas[node_indices[v]]) * dat[
            flownet.weight_attr] for (u, v, dat) in flownet.edges(data=True)}
    else:
        flows = {(u, v): sin(
            thetas[node_indices[u]] - thetas[node_indices[v]]) for (u, v) in flownet.edges()}

    if extra_output:
        omega = _omega(flownet, flows)
        return flows, {'initguess': initguess, 'thetas': thetas, 'omega': omega}
    else:
        return flows


def evolve(flownet, tarr, initguess=None):
    M = nx.incidence_matrix(flownet, oriented=True).toarray()
    Mw = nx.incidence_matrix(flownet, oriented=True, weight=flownet.weight_attr).toarray()
    P = np.array([flownet.node[n]['input'] for n in flownet.nodes()])
    
    if initguess is None:
        initguess = random_stableop_initguess(flownet.number_of_nodes())
    
    return odeint(_kuramoto_ode, initguess, t=tarr, args=(M, Mw, P))
