#!/usr/bin/env python3
"""
Jinja2 模板生成器

将 config 配置字典注入到 Jinja2 模板，生成可执行的 FreeFEM++ 求解脚本。

工作流程：
    1. 接收 config 配置字典（包含边界条件、有限元空间、解析解等）
    2. 将 config 注入到 Jinja2 模板（templates/*.j2）
    3. 渲染主模板和所有 include 文件
    4. 内联所有 include 文件，生成独立的 solver.edp

被 batch_generate.py 调用，用于批量生成freefem脚本。
"""

import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateGenerator:

    def __init__(self, template_dir='templates'):
        self.template_dir = Path(template_dir)

        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_solver(self, config, main_template='solver.edp.j2'):
        """

        Args:
            config (dict): 配置字典，将作为 Jinja2 模板变量注入
                必需字段：
                - boundary_condition: 边界条件（Dirichlet/Electric/Magnetic）
                - domain: 计算域（Square/Circle/Lshaped）
                - mixed_fespace: 混合有限元空间（BDM1/BDM2/...）
                - lagrange_fespace: 拉格朗日有限元空间（P2/P3）
                - exact_solution: 解析解字典（通过 SymPy 计算得到）
            main_template (str): 主模板文件名

        Returns:
            dict: {'solver.edp': 独立的求解器脚本内容}
        """
        # Generate all parts
        main = self.env.get_template(main_template).render(**config)
        arrays = self.env.get_template('includes/arrays.idp.j2').render(**config)
        mesh = self.env.get_template('includes/mesh.idp.j2').render(**config)
        plot = self.env.get_template('includes/plot.idp.j2').render(**config)
        errors = self.env.get_template('includes/errors.idp.j2').render(**config)
        output = self.env.get_template('includes/output.idp.j2').render(**config)

        # Strip headers from includes (remove leading comments)
        def strip_header(content):
            lines = content.split('\n')
            start = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('//') and stripped != '=' * len(stripped):
                    start = i
                    break
            return '\n'.join(lines[start:]).strip() + '\n'

        arrays = strip_header(arrays)
        mesh = strip_header(mesh)
        plot = strip_header(plot)
        errors = strip_header(errors)
        output = strip_header(output)

        # Inline includes via regex substitution
        main = re.sub(r'include "arrays\.idp"[^\n]*\n', arrays + '\n', main)
        main = re.sub(r'include "mesh\.idp"[^\n]*\n', mesh + '\n', main)
        main = re.sub(r'\s*include "plot\.idp"[^\n]*\n', '\n\t' + plot + '\n', main)
        main = re.sub(r'\s*// Error analysis[^\n]*\n\s*include "errors\.idp"[^\n]*\n',
                      '\n    ' + errors + '\n', main)
        main = re.sub(r'// =+\n// Results output[^\n]*\n// =+\ninclude "output\.idp"',
                      output, main)

        return {'solver.edp': main}
