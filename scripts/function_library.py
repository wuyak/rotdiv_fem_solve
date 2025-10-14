#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
函数库
============
存储不同边界条件下的测试函数。
"""

# ============================================================================
# 函数库定义
# ============================================================================

FUNCTION_LIBRARY = {
    # ========================================================================
    # Dirichlet 边界条件 (u = 0 on ∂Ω)
    # ========================================================================
    'Dirichlet': {
        'Trigonometric': {
            'description': '三角函数',
            'domain': ['Square', 'Lshaped'],  # 支持多个域
            'u1': 'sin(pi*x)*sin(pi*y)',
            'u2': 'sin(pi*x)*sin(pi*y)',
        },
        'Bercovier_Engelman': {
            'description': 'Bercovier-Engelman 函数',
            'domain': ['Square'],
            'u1': '-256*y*(y-1)*(2*y-1)*x^2*(x-1)^2',
            'u2': '256*x*(x-1)*(2*x-1)*y^2*(y-1)^2',
        },
        'Ruas': {
            'description': 'Ruas 函数',
            'domain': ['Circle'],
            'u1': 'y*(x^2+y^2-1)',
            'u2': '-x*(x^2+y^2-1)',
        }
    },

    # ========================================================================
    # Electric 边界条件 (u·s = 0, div u = 0 on ∂Ω)
    # ========================================================================
    'Electric': {
        'Trigonometric': {
            'description': '三角函数',
            'domain': ['Square', 'Lshaped'],
            'u1': 'sin(pi*y)*cos(pi*x)',
            'u2': '2*sin(pi*x)*cos(pi*y)',
        },
    },

    # ========================================================================
    # Magnetic 边界条件 (u·n = 0, rot u = 0 on ∂Ω)
    # ========================================================================
    'Magnetic': {
        'Trigonometric': {
            'description': '三角函数',
            'domain': ['Square', 'Lshaped'],
            'u1': 'sin(pi*x)*cos(pi*y)',
            'u2': '2*sin(pi*y)*cos(pi*x)',
        },
    },
}


# ============================================================================
# 数据访问
# ============================================================================

def get_function(boundary_condition: str, function_name: str, domain: str = None) -> dict:
    """
    从函数库中获取测试函数

    参数
    ----
    boundary_condition : str
        边界条件：'Magnetic', 'Electric', 'Dirichlet'
    function_name : str
        函数名称：'Trigonometric', 'Bercovier_Engelman', 'Ruas'
    domain : str, optional
        定义域：'Square', 'Lshaped', 'Circle'

    返回
    ----
    dict : 包含 u1, u2, description, domain 等信息

    异常
    ----
    KeyError : 如果函数组合不存在
    ValueError : 如果函数不支持指定的域
    """
    func_data = FUNCTION_LIBRARY[boundary_condition][function_name].copy()

    if domain and domain not in func_data['domain']:
        raise ValueError(
            f"Function '{function_name}' does not support domain '{domain}'. "
            f"Supported domains: {func_data['domain']}"
        )

    return func_data