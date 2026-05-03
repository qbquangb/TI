"""
inter.py

A small, well-documented Python module that provides:
 - naive Lagrange interpolation evaluation (vectorized with NumPy),
 - barycentric interpolation with precomputed weights and a simple class wrapper,
 - conversion to numpy.poly1d polynomial when nodes are small in number,
 - basic input validation and helpful error messages.

Dependencies: numpy

Usage (summary - see module docstrings for full details):
 - Import functions or use BarycentricInterpolator to cache weights for many evaluations.
 - The module checks for duplicate x_nodes and will raise a ValueError if any are found.
"""

from __future__ import annotations
from typing import Sequence, Optional
import numpy as np
from functools import reduce

__all__ = [
    "lagrange_interpolate",
    "barycentric_interpolate",
    "scipy_interpolate",
    "lagrange_to_poly",
]

def scipy_interpolate(x_nodes: Sequence[float],
                      y_nodes: Sequence[float],
                      x_eval: Sequence[float]) -> np.ndarray:
    """
    Examples:
    --------
    >>> x_nodes = [1, 2, 3]
    >>> y_nodes = [1, 4, 9]  # y = x^2
    >>> x_eval = [1.5, 2.5]
    >>> scipy_interpolate(x_nodes, y_nodes, x_eval)
    array([ 2.25,  6.25])

    >>> x_eval = 10
    >>> scipy_interpolate(x_nodes, y_nodes, x_eval).item()
    100.0
    """
    from scipy.interpolate import BarycentricInterpolator

    interp = BarycentricInterpolator(x_nodes, y_nodes)

    return interp(x_eval)

def _validate_nodes(x_nodes: Sequence[float], y_nodes: Optional[Sequence[float]] = None) -> None:
    """Basic validation: lengths match and x_nodes are distinct."""
    x = np.asarray(x_nodes, dtype=float)
    if y_nodes is not None:
        if len(x) != len(y_nodes):
            raise ValueError("x_nodes and y_nodes must have the same length")
    # check duplicates (within floating tolerance)
    if len(np.unique(x)) != len(x):
        raise ValueError("x_nodes contain duplicate values; nodes must be distinct")

def lagrange_interpolate(x_nodes: Sequence[float],
                         y_nodes: Sequence[float],
                         x_eval: Sequence[float]) -> np.ndarray:
    """
    Naive Lagrange interpolation evaluation.

    Parameters
    ----------
    x_nodes, y_nodes : sequences of length n+1
        Interpolation nodes and corresponding values.
    x_eval : scalar or sequence
        Points at which to evaluate the interpolation polynomial.

    Returns
    -------
    ndarray
        Interpolated values at x_eval (numpy array, same shape as x_eval input).

    Examples
    --------
    >>> x_nodes = [1, 2, 3]
    >>> y_nodes = [1, 4, 9]  # y = x^2
    >>> x_eval = [1.5, 2.5]
    >>> lagrange_interpolate(x_nodes, y_nodes, x_eval)
    array([ 2.25,  6.25])

    >>> x_eval = 10
    >>> lagrange_interpolate(x_nodes, y_nodes, x_eval).item()
    100.0

    Notes
    -----
    This implementation is straightforward and vectorized in NumPy; its cost is O(n^2)
    arithmetic operations for each evaluation grid (but using NumPy reduces Python-loop overhead).
    For repeated evaluations with fixed nodes, prefer BarycentricInterpolator.
    """
    _validate_nodes(x_nodes, y_nodes)
    x_nodes = np.asarray(x_nodes, dtype=float)
    y_nodes = np.asarray(y_nodes, dtype=float)
    x_eval_arr = np.asarray(x_eval, dtype=float)

    n = len(x_nodes)
    P = np.zeros_like(x_eval_arr, dtype=float)

    # Loop over basis polynomials L_j
    for j in range(n):
        num = np.ones_like(x_eval_arr, dtype=float)
        den = 1.0
        xj = x_nodes[j]
        for m in range(n):
            if m == j:
                continue
            xm = x_nodes[m]
            num *= (x_eval_arr - xm)
            den *= (xj - xm)
        P += y_nodes[j] * (num / den)
    return P

def barycentric_weights(x_nodes: Sequence[float]) -> np.ndarray:
    """
    Compute barycentric weights w_j = 1 / prod_{m != j} (x_j - x_m).

    Parameters
    ----------
    x_nodes : sequence
        Distinct nodes.

    Returns
    -------
    ndarray
        1D array of barycentric weights.
    """
    x_nodes = np.asarray(x_nodes, dtype=float)
    _validate_nodes(x_nodes)
    n = len(x_nodes)
    w = np.ones(n, dtype=float)
    # naive O(n^2) computation; fine for moderate n (<= few thousands)
    for j in range(n):
        prod = 1.0
        xj = x_nodes[j]
        for m in range(n):
            if m == j:
                continue
            prod *= (xj - x_nodes[m])
        w[j] = 1.0 / prod
    return w

def barycentric_interpolate(x_nodes: Sequence[float],
                            y_nodes: Sequence[float],
                            x_eval: Sequence[float],
                            w: Optional[Sequence[float]] = None) -> np.ndarray:
    """
    Evaluate barycentric interpolation formula.

    If w (weights) are not supplied, they are computed.

    The function handles the case x equals a node by returning the exact y value
    (avoids division by zero).

    Parameters
    ----------
    x_nodes, y_nodes : sequences of length n+1
        Interpolation nodes and corresponding values.
    x_eval : scalar or sequence
        Points at which to evaluate the interpolation polynomial.
    w : optional sequence of length n+1
        Barycentric weights. If None, they are computed from x_nodes.
    Returns
    -------
    ndarray
        Interpolated values at x_eval (numpy array, same shape as x_eval input).
    Examples
    --------
    >>> x_nodes = [1, 2, 3]
    >>> y_nodes = [1, 4, 9]  # y = x^2
    >>> x_eval = [1.5, 2.5]
    >>> barycentric_interpolate(x_nodes, y_nodes, x_eval)
    array([ 2.25,  6.25])

    >>> x_eval = 10
    >>> barycentric_interpolate(x_nodes, y_nodes, x_eval).item()
    100.0
    """
    _validate_nodes(x_nodes, y_nodes)
    x_nodes = np.asarray(x_nodes, dtype=float)
    y_nodes = np.asarray(y_nodes, dtype=float)
    x_eval = np.asarray(x_eval, dtype=float)

    if w is None:
        w = barycentric_weights(x_nodes)
    else:
        w = np.asarray(w, dtype=float)
        if len(w) != len(x_nodes):
            raise ValueError("weights length must match number of nodes")

    P = np.empty_like(x_eval, dtype=float)

    # Evaluate one-by-one because we need to check if x equals any node exactly
    for i, x in enumerate(x_eval):
        diffs = x - x_nodes
        # check exact match (within machine precision)
        idx = np.where(np.abs(diffs) == 0)[0]
        if idx.size:
            P[i] = y_nodes[idx[0]]
            continue
        numer = np.sum(w * y_nodes / diffs)
        denom = np.sum(w / diffs)
        P[i] = numer / denom
    return P

def lagrange_to_poly(x_nodes: Sequence[float], y_nodes: Sequence[float]) -> np.poly1d:
    """
    Expand the Lagrange form to an explicit polynomial (numpy.poly1d).

    This is convenient for small n when you want coefficients or to symbolically inspect
    the polynomial. For large n this becomes expensive (polynomial multiplication cost).

    Parameters
    ----------
    x_nodes, y_nodes : sequences of length n
        Interpolation nodes and corresponding values.

    Returns
    -------
    np.poly1d
        Polynomial representation of the Lagrange interpolant.

    Examples
    --------
    >>> x_nodes = [1, 2, 3]
    >>> y_nodes = [1, 4, 9]  # y = x^2
    >>> lagrange_to_poly(x_nodes, y_nodes)
    poly1d([ 1.,  0.,  0.])  # which is x^2
    """
    _validate_nodes(x_nodes, y_nodes)
    x_nodes = np.asarray(x_nodes, dtype=float)
    y_nodes = np.asarray(y_nodes, dtype=float)
    n = len(x_nodes)

    poly = np.poly1d([0.0])
    for j in range(n):
        # numerator polynomial: prod_{m!=j} (x - x_m)
        factors = [np.poly1d([1.0])]
        for m in range(n):
            if m == j:
                continue
            factors.append(np.poly1d([1.0, -x_nodes[m]]))
        numer = reduce(lambda a, b: np.polymul(a, b), factors)
        den = 1.0
        for m in range(n):
            if m == j:
                continue
            den *= (x_nodes[j] - x_nodes[m])
        L_j = numer / den
        poly = poly + y_nodes[j] * L_j

    # clean tiny floating coefficients
    coeffs = np.array(poly.coeffs)
    coeffs[np.abs(coeffs) < 1e-6] = 0.0
    return np.poly1d(coeffs)

class BarycentricInterpolator2:
    """
    Simple class wrapper that caches barycentric weights for repeated evaluations.

    Example (informal):
        interp = BarycentricInterpolator2(x_nodes, y_nodes)
        y = interp.evaluate(x_grid)
        poly = interp.to_poly()
    """

    def __init__(self, x_nodes: Sequence[float], y_nodes: Sequence[float]):
        _validate_nodes(x_nodes, y_nodes)
        self.x_nodes = np.asarray(x_nodes, dtype=float)
        self.y_nodes = np.asarray(y_nodes, dtype=float)
        self._w = barycentric_weights(self.x_nodes)

    @property
    def weights(self) -> np.ndarray:
        return self._w

    def evaluate(self, x_eval: Sequence[float]) -> np.ndarray:
        """Evaluate interpolant at x_eval (vectorized wrapper)."""
        return barycentric_interpolate(self.x_nodes, self.y_nodes, x_eval, w = self._w)

    def to_poly(self) -> np.poly1d:
        """Return the expanded polynomial as numpy.poly1d."""
        return lagrange_to_poly(self.x_nodes, self.y_nodes)

if __name__ == "__main__":
    x_nodes = [1, 2, 3, 4, 5]
    y_nodes = [xi * xi for xi in x_nodes]
    interp = BarycentricInterpolator2(x_nodes, y_nodes)
    xgrid = np.linspace(0, 6, 61)
    ygrid = interp.evaluate(xgrid)
    poly = interp.to_poly()
    print("Interpolating polynomial:")
    print(poly)
    print("Evaluated at xgrid:", ygrid)