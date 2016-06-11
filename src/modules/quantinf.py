# -*- coding: utf-8 -*-
"""
This module implements a number of quantum information functions
in QuTiP (Quantum Toolbox in Python)

Project: Investigation of Entanglement Measures in QuTiP
         (IIUI, Fall 2015)

@author: Muhammad Saad <muhammad.saad@yandex.com>
"""

__all__ = ['purity','ispure','purity_of_reduced','ismixed_reduced',
        'peres_horodecki_bipartite','schmidt_decomposition', 'dist_kl',
        'entropy_entg', 'entropy_linear_entg', 'negativity', 'log_neg',
        'linear_entropy', 'entropy_renyi', 'entropy_renyi_entg' ]

from qutip import ( Qobj, ket2dm, entropy_vn, ptrace, partial_transpose )
from numpy import log2
import numpy as np

def purity(dm):
    """ Calculates trace of density matrix squared
    
    Parameters
    ----------
    dm: qobj/array-like
        Input density matrix
    
    Returns
    -------
    purity:
        Purity of the state. 1 for pure, 0.5 for maximally mixed.
    
    """
    if dm.type == 'ket':
        dm = ket2dm(dm)
    if dm.type != 'oper':
        raise TypeError("Input must be a state ket or density matrix")
    purity = (dm**2).tr()
    return purity

def purity_of_reduced(rho):
    """ Calculates trace of reduced density matrix square
    
    Parameters
    ----------
    dm: qobj/array-like
        Input density matrix
    
    Returns
    -------
    purityreduced:
        Purity of the reduced DM. 1 for pure, 0.5 for maximally mixed.
    
    """
    rhopartial = ptrace(rho,0)
    purityreduced = purity(rhopartial)
    return purityreduced

def ispure(dm):
    """ Checks whether or not a density matrix represents a pure state
    
    Parameters
    ----------
    dm : qobj/array-like
        Density operator representing the state.
    
    -------
    pure : bool
        Whether or not the state is pure. True: Pure, False: Mixed.
        
    """
    if np.round(purity(dm),8) == 1:
        return True
    else:
        return False

def ismixed_reduced(dm):
    """ One way to check for entanglement is that the reduced density
    matrix is mixed. This function checks for that criterion.
    
    Parameters
    ----------
    dm : qobj/array-like
        Density operator representing the state.
    
    -------
    mixed : bool
        Whether or not the reduced DM is mixed. True: Mixed, False: Pure
        
    """
    if np.round(purity_of_reduced(dm),8) != 1:
        return True
    else:
        return False

def schmidt_decomposition(vec):
    """ Schmidt decomposition of a bipartite vector
    Based on the implementation in QETLAB 0.9
    which was written by Nathaniel Johnston (nathaniel@njohnston.ca)
    and as of this port, last updated on December 1, 2012
    
    Parameters
    ----------
    vec : qobj, ket vector of product state
        ket vector representing the bipartite state
    
    -------
    Returns:
    [s, u, v]
    s : list of floats
        Schmidt coefficients
    u : list of Qobj
        list of left Schmidt vectors of ket
    v : list of Qobj
        list of right Schmidt vectors of ket
        
    """
    if vec.type != 'ket':
        raise TypeError("Input must be a ket vector.")
    if len(vec.dims[0])==1:
        raise TypeError("Input must be a joint state.")
    
    dim = vec.dims[0][0]
    vecnp = vec.full()
    vecnpr = np.reshape(vecnp,[dim,dim])
    um,s,vm = np.linalg.svd(vecnpr)
    
    s = list(s)
    
    def extract_vecs(mat):
        veclist = list()
        for j in range(mat.shape[1]):
            veclist.append(Qobj(mat[:,j]))
        return veclist
    u = extract_vecs(um)
    v = extract_vecs(vm)
    
    return [s,u,v]

def peres_horodecki_bipartite(rho, mask=[0,1]):
    """ Tests the given bipartite state for Peres-Horodecki criterion
    
    Parameters
    ----------
    rho: qobj/array-like
        Density operator for the state
    mask: list of int, length 2
        mask used for partial transpose
    
    Returns
    -------
    isentangled: bool
        True for entangled, False for disentangled
    
    """
    if rho.type != 'oper':
        raise TypeError("Input must be a density matrix")
    rhopt = partial_transpose(rho,mask)
    rhopt_eigs = rhopt.eigenenergies()
    if min(rhopt_eigs) < 0:
        isentangled = True
    else:
        isentangled = False
    return isentangled

def entropy_entg(rho, base=2):
    """ Calculates the entropy of entanglement of a density matrix
    
    Parameters:
    -----------
    rho : qobj/array-like
        Input density matrix
    base:
        Base of log
    
    Returns:
    --------
    ent_entg: Entropy of Entanglement
    
    """
    if rho.type == 'ket':
        rho = ket2dm(rho)
    if rho.type != 'oper':
        raise TypeError("Input must be density matrix")
    rhopartial = ptrace(rho,0)
    ent_entg = entropy_vn(rhopartial,base)
    return ent_entg

def linear_entropy(dm, normalize=False):
    """ Returns the linear entropy of a state.
    
    Parameters
    ----------
    dm : qobj/array-like
        Density operator representing the state.
    normalize : bool
        Optional argument to normalize linear entropy such that the
        completely mixed state has LE = 1 rather than 1-1/d. [1]
        Default: False
    
    ----------
    le : float
        Linear entropy
        
    >>> 
    
    """
    if dm.type not in ('oper','ket'):
        raise TypeError("Input must be a Qobj representing a state.")
    if dm.type=='ket':
        dm = ket2dm(dm)
    
    le = 1 - (dm**2).tr()
    if normalize:
        d = dm.shape[0]
        le = le * d/(d-1)
    return le

def entropy_linear_entg(rho, normalize=True):
    """ Calculates the linear entropy of entanglement of a density matrix
    
    Parameters:
    -----------
    rho : qobj/array-like
        Input density matrix
    
    Returns:
    --------
    linent_entg: Linear Entropy of Entanglement
    
    """
    if rho.type == 'ket':
        rho = ket2dm(rho)
    if rho.type != 'oper':
        raise TypeError("Input must be density matrix")
    rhopartial = ptrace(rho,0)
    linent_entg = linear_entropy(rhopartial,normalize)
    return linent_entg

def entropy_renyi(rho,alpha):
    """ Calculate Renyi entropy of the density matrix with given index
    (Currently limited to 2-level systems)
    
    Parameters
    ----------
    dm: qobj/array-like
        Input density matrix
        
    alpha: Renyi index alpha
    
    Returns
    -------
    ent_rn: Renyi Entropy
    
    """
    if rho.type != 'oper':
        raise TypeError("Input must be a density matrix")
    qi = rho.eigenenergies()
    
    if alpha == 1:
        ent_rn = entropy_vn(rho,2)
    elif alpha >= 0:
        ent_rn = ( 1/(1-alpha) ) * log2 ( sum( qi**alpha ) )
    else:
        raise ValueError("alpha must be a non-negative number")
    return ent_rn

def entropy_renyi_entg(rho,alpha):
    """ Calculate Renyi entropy of entanglement for the DM with given index
    (Currently limited to 2-level systems)
    
    Parameters
    ----------
    dm: qobj/array-like
        Input density matrix
        
    alpha: Renyi index alpha
    
    Returns
    -------
    ent_rn_entg: Renyi Entropy of Entanglement
    
    """
    rhopartial = ptrace(rho,0)
    ent_rn_entg = entropy_renyi(rhopartial,alpha)
    return ent_rn_entg

def negativity(rho,mask=[1,0]):
    """ Calculate the negativity for a density matrix
    
    Parameters:
    -----------
    rho : qobj/array-like
        Input density matrix
    
    Returns:
    --------
    neg : Negativity
    
    """
    if rho.type != 'oper':
        raise TypeError("Input must be a density matrix")
    rhopt = partial_transpose(rho,mask)
    neg = ( rhopt.norm() - 1 ) / 2
    return neg

def log_neg(rho,mask=[1,0]):
    """ Calculate the logarithmic negativity for a density matrix
    
    Parameters:
    -----------
    rho : qobj/array-like
        Input density matrix
    
    Returns:
    --------
    logneg: Logarithmic Negativity
    
    """
    if rho.type != 'oper':
        raise TypeError("Input must be a density matrix")
    rhopt = partial_transpose(rho,mask)
    logneg = log2( rhopt.norm() )
    return logneg

def dist_kl(rho, sgm):
    """ Calculates the Kullback-Leibler distance (a.k.a. relative entropy)
    between DMs rho and sgm representing two-level systems.
    
    Parameters
    ----------
    rho : qobj/array-like
        First density operator.

    sgm : qobj/array-like
        Second density operator.

    Returns
    -------
    kldist : float
        Relative Entropy between rho and sgm.
    
    """
    if rho.type != 'oper' or sgm.type != 'oper':
        raise TypeError("Inputs must be density matrices..")
    
    ent_vn = entropy_vn(rho,2)
    
    r_eigs = rho.eigenenergies()
    s_eigs = sgm.eigenenergies()
    # too small negtive values may give trouble
    s_eigs = np.round(s_eigs,8)
    
    kldist = -ent_vn
    for pj, qj in zip(r_eigs,s_eigs):
        if qj==0:
            pass
        else:
            kldist -= pj * log2(qj)
            
    kldist = abs(kldist)
    return kldist

