#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 Stephane Caron <stephane.caron@normalesup.org>
#
# This file is part of qpsolvers.
#
# qpsolvers is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# qpsolvers is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with qpsolvers. If not, see <http://www.gnu.org/licenses/>.

from numpy import concatenate, eye, ndarray

available_solvers = []
dense_solvers = []
sparse_solvers = []

# CVXOPT
# ======

try:
    from .cvxopt_ import cvxopt_set_verbosity
    from .cvxopt_ import cvxopt_solve_qp

    available_solvers.append('cvxopt')
    dense_solvers.append('cvxopt')
except ImportError:
    def cvxopt_set_verbosity(*args, **kwargs):
        pass


    def cvxopt_solve_qp(*args, **kwargs):
        raise ImportError("CVXOPT not found")

# CVXPY
# =====

try:
    from .cvxpy_ import cvxpy_set_verbosity
    from .cvxpy_ import cvxpy_solve_qp

    available_solvers.append('cvxpy')
    sparse_solvers.append('cvxpy')
except ImportError:
    def cvxpy_set_verbosity(*args, **kwargs):
        pass


    def cvxpy_solve_qp(*args, **kwargs):
        raise ImportError("CVXPY not found")

# ECOS
# ====

try:
    from .ecos_ import ecos_set_verbosity
    from .ecos_ import ecos_solve_qp

    available_solvers.append('ecos')
    dense_solvers.append('ecos')  # considered dense as it calls cholesky(P)
except ImportError:
    def ecos_set_verbosity(*args, **kwargs):
        pass


    def ecos_solve_qp(*args, **kwargs):
        raise ImportError("ECOS not found")

# Gurobi
# ======

try:
    from .gurobi_ import gurobi_set_verbosity
    from .gurobi_ import gurobi_solve_qp

    available_solvers.append('gurobi')
    sparse_solvers.append('gurobi')
except ImportError:
    def gurobi_set_verbosity(*args, **kwargs):
        pass


    def gurobi_solve_qp(*args, **kwargs):
        raise ImportError("Gurobi not found")

# Mosek
# =====

try:
    from .mosek_ import mosek_set_verbosity
    from .mosek_ import mosek_solve_qp

    available_solvers.append('mosek')
    sparse_solvers.append('mosek')
except ImportError:
    def mosek_set_verbosity(*args, **kwargs):
        pass


    def mosek_solve_qp(*args, **kwargs):
        raise ImportError("mosek not found")

# OSQP
# ====

try:
    from .osqp_ import osqp_set_verbosity
    from .osqp_ import osqp_solve_qp

    available_solvers.append('osqp')
    sparse_solvers.append('osqp')
except ImportError:
    def osqp_set_verbosity(*args, **kwargs):
        pass


    def osqp_solve_qp(*args, **kwargs):
        raise ImportError("osqp not found")

# qpOASES
# =======

try:
    from .qpoases_ import qpoases_set_verbosity
    from .qpoases_ import qpoases_solve_qp

    available_solvers.append('qpoases')
    dense_solvers.append('qpoases')
except ImportError:
    def qpoases_set_verbosity(*args, **kwargs):
        pass


    def qpoases_solve_qp(*args, **kwargs):
        raise ImportError("qpOASES not found")

# quadprog
# ========

try:
    from .quadprog_ import quadprog_set_verbosity
    from .quadprog_ import quadprog_solve_qp

    available_solvers.append('quadprog')
    dense_solvers.append('quadprog')
except ImportError:
    def quadprog_set_verbosity(*args, **kwargs):
        pass


    def quadprog_solve_qp(*args, **kwargs):
        raise ImportError("quadprog not found")


def check_problem(P, q, G, h, A, b, lb, ub):
    """
    Check that problem matrices and vectors are correctly defined.

    Parameters
    ----------
    P : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Symmetric quadratic-cost matrix (most solvers require it to be definite
        as well).
    q : numpy.array
        Quadratic-cost vector.
    G : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Linear inequality matrix.
    h : numpy.array
        Linear inequality vector.
    A : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Linear equality matrix.
    b : numpy.array
        Linear equality vector.
    lb: numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Lower bound constraint vector.
    ub: numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Upper bound constraint vector.
    """
    if G is None and h is not None:
        raise ValueError("incomplete inequality constraint (missing h)")
    elif G is not None and h is None:
        raise ValueError("incomplete inequality constraint (missing G)")
    if A is None and b is not None:
        raise ValueError("incomplete equality constraint (missing b)")
    elif A is not None and b is None:
        raise ValueError("incomplete equality constraint (missing A)")


def solve_qp(P, q, G=None, h=None, A=None, b=None, lb=None, ub=None,
             solver='quadprog', initvals=None, sym_proj=False, verbose=False):
    """
    Solve a Quadratic Program defined as:

        minimize
            (1/2) * x.T * P * x + q.T * x

        subject to
            lb <= x <= ub
            G * x <= h
            A * x == b

    using one of the available QP solvers.

    Parameters
    ----------
    P : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Symmetric quadratic-cost matrix (most solvers require it to be definite
        as well).
    q : numpy.array
        Quadratic-cost vector.
    G : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Linear inequality matrix.
    h : numpy.array
        Linear inequality vector.
    A : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Linear equality matrix.
    b : numpy.array
        Linear equality vector.
    lb: numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Lower bound constraint vector.
    ub: numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Upper bound constraint vector.
    solver : string, optional
        Name of the QP solver, to choose in ``qpsolvers.available_solvers``.
    initvals : array, optional
        Vector of initial `x` values used to warm-start the solver.
    sym_proj : bool, optional
        Set to `True` when the `P` matrix provided is not symmetric.
    verbose : bool, optional
        Set to `True` to print out extra information.

    Returns
    -------
    x : array or None
        Optimal solution if found, None otherwise.

    Notes
    -----
    In quadratic programming, the matrix `P` should be symmetric. Many solvers
    (including CVXOPT, OSQP and quadprog) leverage this property and may return
    erroneous results when it is not the case. You can set ``sym_proj=True`` to
    project `P` on its symmetric part, at the cost of some computation time.
    """
    if sym_proj:
        P = .5 * (P + P.transpose())
    if type(A) is ndarray and A.ndim == 1:
        A = A.reshape((1, A.shape[0]))
    if type(G) is ndarray and G.ndim == 1:
        G = G.reshape((1, G.shape[0]))
    check_problem(P, q, G, h, A, b, lb, ub)
    if lb is not None:
        if G is None:
            G = -eye(len(q))
            h = -lb
        else:  # G is not None and h is not None
            G = concatenate((G, -eye(len(q))), 0)
            h = concatenate((h, -lb))
    if ub is not None:
        if G is None:
            G = eye(len(q))
            h = ub
        else:  # G is not None and h is not None
            G = concatenate((G, eye(len(q))), 0)
            h = concatenate((h, ub))
    if solver == 'cvxopt':
        cvxopt_set_verbosity(verbose)
        return cvxopt_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'cvxpy':
        cvxpy_set_verbosity(verbose)
        return cvxpy_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'ecos':
        ecos_set_verbosity(verbose)
        return ecos_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'gurobi':
        gurobi_set_verbosity(verbose)
        return gurobi_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'mosek':
        mosek_set_verbosity(verbose)
        return mosek_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'osqp':
        osqp_set_verbosity(verbose)
        return osqp_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'qpoases':
        qpoases_set_verbosity(verbose)
        return qpoases_solve_qp(P, q, G, h, A, b, initvals=initvals)
    elif solver == 'quadprog':
        quadprog_set_verbosity(verbose)
        return quadprog_solve_qp(P, q, G, h, A, b, initvals=initvals)
    raise Exception("solver '%s' not recognized" % solver)


def solve_safer_qp(P, q, G, h, sw, reg=1e-8, solver='mosek', initvals=None,
                   sym_proj=False):
    """
    Solve the Quadratic Program defined as:

        minimize
            (1/2) * x.T * P * x + q.T * x + (1/2) reg |s|^2 - sw 1^T s

        subject to
            G * x <= h

    Slack variables `s` are increased by an additional term in the cost
    function, so that the solution of this "safer" QP is further inside the
    constraint region.

    Parameters
    ----------
    P : numpy.array
        Symmetric quadratic-cost matrix.
    q : numpy.array
        Quadratic-cost vector.
    G : numpy.array
        Linear inequality matrix.
    h : numpy.array
        Linear inequality vector.
    sw : scalar
        Weight of the linear cost on slack variables. Higher values bring the
        solution further inside the constraint region but override the
        minimization of the original objective.
    reg : scalar
        Regularization term :math:`(1/2) \\epsilon` in the cost function. Set
        this parameter as small as possible (e.g. 1e-8), and increase it in
        case of numerical instability.
    solver : string, optional
        Name of the QP solver to use (default is MOSEK).
    initvals : array, optional
        Vector of initial `x` values used to warm-start the solver.
    sym_proj : bool, optional
        Set to `True` when the `P` matrix provided is not symmetric.

    Returns
    -------
    x : array, shape=(n,)
        Optimal solution to the relaxed QP, if found.

    Raises
    ------
    ValueError
        If the QP is not feasible.

    Notes
    -----
    This method can be found in the Inverse Kinematics resolution of Nozawa et
    al. (Humanoids 2016). It also appears in earlier works such as the
    "optimally safe" tension distribution algorithm of Borgstrom et al. (IEEE
    Transactions on Robotics, 2009).
    """
    assert solver in dense_solvers, "only available for dense solvers, for now"
    from numpy import eye, hstack, ones, vstack, zeros
    n, m = P.shape[0], G.shape[0]
    E, Z = eye(m), zeros((m, n))
    P2 = vstack([hstack([P, Z.T]), hstack([Z, reg * eye(m)])])
    q2 = hstack([q, -sw * ones(m)])
    G2 = hstack([Z, E])
    h2 = zeros(m)
    A2 = hstack([G, -E])
    b2 = h
    x = solve_qp(
        P2, q2, G2, h2, A2, b2, solver=solver, initvals=initvals,
        sym_proj=sym_proj)
    return x[:n]


__all__ = [
    'available_solvers',
    'cvxopt_solve_qp',
    'cvxpy_solve_qp',
    'dense_solvers',
    'gurobi_solve_qp',
    'mosek_solve_qp',
    'qpoases_solve_qp',
    'quadprog_solve_qp',
    'solve_qp',
    'solve_safer_qp',
    'sparse_solvers',
]
