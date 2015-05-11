import numpy as np
from scipy.integrate import odeint 
import networkx as nx
from math import sin

def _kuramoto_ode(th,t, M_I,M_I_w, P): 
    """
    th: theta, array with size=nnodes
    t: time
    M_I: unweighted oriented incidence matrix
    M_I_W: weighted oriented incidence matrix
    P: Power production at each node
    """
    return P-np.dot(M_I_w, np.sin(np.dot(M_I.T, th)))




def _try_find_fps(ntry,M,Mw, P, tmax=200, tol=10e-4, initguess=None):
    """
    ntry: number of initial conditions that will be tried to reach a fixed point
    tol: the odesolver ends when the norm of the vector at different stages get less than this
    """


    assert(M.shape[0]==P.shape[0])  #The way it's supposed to be done...
    

    size=P.shape[0]
    
    #trying to detect if converged
    #the individual oscillators, if decoupled, will accelerate with constant torque P_j. 
    #therefore, in time t, starting from 0, it will reach angular vel 0.5P_j t**2.
    #let's assume 10*sqrt(2/P) is a reasonable time for them to complete multiple full 2*pi oscillations

    large_time=10*np.sqrt(2.0/np.max(P))
   
    if initguess:
        sol=odeint(_kuramoto_ode, initguess, t=[0, tmax,tmax+large_time+np.random.rand(),tmax+2*large_time+np.random.rand()], args=(M,Mw,P))
        if np.linalg.norm(sol[-1,:]-sol[-2,:])<tol and np.linalg.norm(sol[-2,:]-sol[-3,:])<tol:
            return sol[-1], initguess
        else:
            return None

   
    for ntry in range(ntry):
        initguess=np.random.uniform(0,np.pi/2, size)
    
        sol=odeint(_kuramoto_ode, initguess, t=[0, tmax,tmax+large_time+np.random.rand(),tmax+2*large_time+np.random.rand()], args=(M,Mw,P))
        if np.linalg.norm(sol[-1,:]-sol[-2,:])<tol and np.linalg.norm(sol[-2,:]-sol[-3,:])<tol:
            return sol[-1], initguess
    return None


def fixed_point(flownet, initguess=None):
    M=np.array(nx.incidence_matrix(flownet, oriented=True))
    Mw=np.array(nx.incidence_matrix(flownet, oriented=True, weight=flownet.weight_attr))

    P=np.array([flownet.node[n]['input'] for n in flownet.nodes()])
    
    thetas, initguess=_try_find_fps(100,M,Mw,P, initguess=initguess)


    node_indices={node:idx for idx,node in enumerate(flownet.nodes())}

    if flownet.weight_attr:
        flows={(u,v):sin(thetas[node_indices[u]]-thetas[node_indices[v]])*dat[flownet.weight_attr] for (u,v,dat) in flownet.edges()}
    else:
        flows={(u,v):sin(thetas[node_indices[u]]-thetas[node_indices[v]]) for (u,v) in flownet.edges()}

    return flows, {'initguess':initguess}

