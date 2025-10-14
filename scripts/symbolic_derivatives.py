#!/usr/bin/env python3
"""
Symbolic Derivatives Calculator for FreeFEM Exact Solutions

This module automatically computes all required derivatives for
finite element error analysis using symbolic differentiation.

Based on the operators:
- For vector u = (u1, u2):
  * div(u) = ∂u1/∂x + ∂u2/∂y
  * rot(u) = ∂u2/∂x - ∂u1/∂y  (2D rotation)

- For scalar γ:
  * grad(γ) = (∂γ/∂x, ∂γ/∂y)
  * curl(γ) = (∂γ/∂y, -∂γ/∂x)
"""

import sympy as sp
from sympy import sympify
from typing import Dict


class ExactSolutionDerivatives:
    """Compute all derivatives for exact solutions"""

    def __init__(self):
        # Define symbolic variables
        self.x = sp.Symbol('x')
        self.y = sp.Symbol('y')

    def parse_expression(self, expr_str: str) -> sp.Expr:
        """Parse string expression to sympy expression

        Converts FreeFEM syntax (^) to Python (**) and evaluates safely.
        """
        expr_str = expr_str.replace('^', '**')

        local_dict = {
            'x': self.x,
            'y': self.y,
            'pi': sp.pi,
            'sin': sp.sin,
            'cos': sp.cos,
            'exp': sp.exp,
            'log': sp.log,
            'sqrt': sp.sqrt,
        }

        try:
            return sympify(expr_str, locals=local_dict)
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{expr_str}': {e}")

    def to_freefem_string(self, expr: sp.Expr) -> str:
        """Convert sympy expression to FreeFEM syntax"""
        result = str(expr)
        result = result.replace('sp.pi', 'pi')
        result = result.replace('**', '^')
        return result

    def compute_vector_derivatives(self,
                                   u1_expr: str,
                                   u2_expr: str) -> Dict[str, str]:
        """
        Compute all derivatives for a vector field u = (u1, u2)

        Args:
            u1_expr: String expression for u1 (e.g., "sin(pi*y)*cos(pi*x)")
            u2_expr: String expression for u2

        Returns:
            Dictionary with all derivatives in FreeFEM syntax:
            - u1exact, u2exact: Original expressions
            - u1x, u1y, u2x, u2y: First derivatives
            - rotu, divu: Rotation and divergence
            - rotu_x, rotu_y, divu_x, divu_y: Derivatives of rot and div
            - f1, f2: Forcing terms (-Δu)
        """
        # Parse expressions
        u1 = self.parse_expression(u1_expr)
        u2 = self.parse_expression(u2_expr)

        # First derivatives
        u1x = sp.diff(u1, self.x)
        u1y = sp.diff(u1, self.y)
        u2x = sp.diff(u2, self.x)
        u2y = sp.diff(u2, self.y)

        # Divergence: div(u) = ∂u1/∂x + ∂u2/∂y
        divu = u1x + u2y

        # Rotation (2D): rot(u) = ∂u2/∂x - ∂u1/∂y
        rotu = u2x - u1y

        # Second derivatives (for Laplacian)
        u1xx = sp.diff(u1x, self.x)
        u1yy = sp.diff(u1y, self.y)
        u2xx = sp.diff(u2x, self.x)
        u2yy = sp.diff(u2y, self.y)

        # Forcing terms: f = -Δu = -(∂²u/∂x² + ∂²u/∂y²)
        f1 = -(u1xx + u1yy)
        f2 = -(u2xx + u2yy)

        # Derivatives of divergence: grad(div)
        divu_x = sp.diff(divu, self.x)
        divu_y = sp.diff(divu, self.y)

        # Derivatives of rotation: grad(rot)
        rotu_x = sp.diff(rotu, self.x)
        rotu_y = sp.diff(rotu, self.y)

        # Simplify and return
        results = {
            'u1exact': sp.simplify(u1),
            'u2exact': sp.simplify(u2),
            'u1x': sp.simplify(u1x),
            'u1y': sp.simplify(u1y),
            'u2x': sp.simplify(u2x),
            'u2y': sp.simplify(u2y),
            'divu': sp.simplify(divu),
            'rotu': sp.simplify(rotu),
            'divux': sp.simplify(divu_x),
            'divuy': sp.simplify(divu_y),
            'rotux': sp.simplify(rotu_x),
            'rotuy': sp.simplify(rotu_y),
            'f1': sp.simplify(f1),
            'f2': sp.simplify(f2),
        }

        # Convert to FreeFEM strings
        return {key: self.to_freefem_string(val)
                for key, val in results.items()}
