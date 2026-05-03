import math
import numpy as np
from sympy import symbols, sympify, sin, cos, exp

def central_diff(f, x0, eps):
    """Central difference approx: (f(x0+eps)-f(x0-eps))/(2*eps)."""
    return (f(x0 + eps) - f(x0 - eps)) / (2.0 * eps)

def approx_derivative(eps=1e-6):
    """
    Approximate derivative using central difference.
    If eps is None, choose eps ~ machine_epsilon^(1/3) * max(1,|x|).
    eps có thể đặt bằng None hoặc 1e-4
    Returns (approx_value, eps_used).
    """
    x = symbols('x')
    expr = sympify(input("Enter the function f(x): ").strip().lower())
    print(f"Function entered: {expr}")
    x0 = float(input("Enter the point x0 to evaluate the derivative: ").strip())
    if eps is None:
        mach_eps = np.finfo(float).eps
        eps = mach_eps ** (1/3) * max(1.0, abs(x0))
    approx_d = central_diff(lambda v: expr.subs(x, v).evalf(), x0, eps)
    print(f"Approximate derivative at x={x0} is {approx_d} with eps={eps}")
    return approx_d, eps

if __name__ == "__main__":
    approx_derivative(eps=1e-6)  # Bạn có thể thay None bằng 1e-4 để thử nghiệm với eps cố định