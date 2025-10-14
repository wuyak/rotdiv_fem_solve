#!/usr/bin/env python3
"""
编译FreeFEM++求解器

将抽象的变分问题配置编译为可执行的FreeFEM++ .edp文件。
使用Jinja2模板引擎，从函数库加载测试函数，通过SymPy自动求导，
生成完整的有限元求解器代码。

Usage:
    # 生成所有freefem求解文件
    python scripts/batch_generate.py

    # 按边界条件筛选
    python scripts/batch_generate.py --filter Dirichlet    # 仅Dirichlet边界

    # 按定义域筛选
    python scripts/batch_generate.py --filter Square       # 仅方形域

    # 按函数名筛选（使用缩写）
    python scripts/batch_generate.py --filter Trig         # Trigonometric 函数
    python scripts/batch_generate.py --filter BercEng      # Bercovier_Engelman 函数

    # 按有限元空间筛选
    python scripts/batch_generate.py --filter BDM2         # 所有BDM2空间

    # 调整并行数
    python scripts/batch_generate.py --parallel 8          # 使用8个并行任务

Note:
    过滤机制：
    - 使用简单的子字符串匹配（Python 'in' 运算符）
    - 过滤字符串格式：{boundary_condition}_{function_abbr}_{domain}/{fespace}
    - 示例：Dirichlet_Trig_Square/BDM1_P2

    函数名使用缩写：
    - Trigonometric → Trig
    - Bercovier_Engelman → BercEng
    - Ruas → Ruas

    如需复杂过滤，可以多次运行不同的 --filter 或使用 shell 管道
"""

import argparse
from pathlib import Path
from template_generator import TemplateGenerator
from parallel_runner import parallel_map_with_progress
from function_library import FUNCTION_LIBRARY, get_function
from symbolic_derivatives import ExactSolutionDerivatives

# =============================================================================
# 有限元空间组合配置
# =============================================================================
# 定义不同边界条件下使用的有限元空间组合
FESPACE_COMBINATIONS = {
    'Dirichlet': [
        ('BDM1', 'P2'),
        ('BDM2', 'P3'),
    ],
    'Electric': [
        ('BDM1', 'P2'),
        ('BDM2', 'P3'),
        ('BDM1Ortho', 'P2'),
        ('BDM2Ortho', 'P3'),
    ],
    'Magnetic': [
        ('BDM1', 'P2'),
        ('BDM2', 'P3'),
        ('BDM1Ortho', 'P2'),
        ('BDM2Ortho', 'P3'),
    ],
}

# =============================================================================
# 任务生成（从函数库自动生成）
# =============================================================================
def generate_tasks():
    """
    从函数库自动生成所有实验任务

    遍历FUNCTION_LIBRARY中的所有(边界条件, 函数名, 域)组合，
    为每个组合生成对应的有限元空间任务。

    Returns:
        list: 任务配置列表
    """
    tasks = []

    # 函数名称缩写映射（用于生成简洁的任务名）
    function_abbr = {
        'Trigonometric': 'Trig',
        'Bercovier_Engelman': 'BercEng',
        'Ruas': 'Ruas',
    }

    # 遍历函数库中的所有组合
    for boundary_condition, functions in FUNCTION_LIBRARY.items():
        for function_name, func_data in functions.items():
            # 获取该函数支持的所有域
            domains = func_data['domain']

            # 获取该边界条件使用的有限元空间组合
            fespace_combinations = FESPACE_COMBINATIONS[boundary_condition]

            # 为每个域和有限元空间组合生成任务
            for domain in domains:
                for mixed_fespace, lagrange_fespace in fespace_combinations:
                    # 生成任务名称（简洁格式）
                    func_short = function_abbr.get(function_name, function_name)
                    task_name = f'{boundary_condition}_{func_short}_{domain}'

                    tasks.append({
                        'name': task_name,
                        'fespace_name': f'{mixed_fespace}_{lagrange_fespace}',
                        'boundary_condition': boundary_condition,
                        'function_name': function_name,
                        'domain': domain,
                        'mixed_fespace': mixed_fespace,
                        'lagrange_fespace': lagrange_fespace,
                    })

    return tasks


def generate_single_task(task_config, output_dir='output'):
    """
    生成单个FreeFEM++脚本

    Args:
        task_config: 任务配置字典
        output_dir: 输出目录

    Returns:
        (success: bool, message: str): 成功标志和结果消息
    """
    try:
        # 使用任务配置
        config = task_config

        # 从函数库加载测试函数
        func_data = get_function(
            config['boundary_condition'],
            config['function_name'],
            config['domain']
        )

        # 通过 SymPy 计算freefem文件所需的解析解
        calc = ExactSolutionDerivatives()
        config['exact_solution'] = calc.compute_vector_derivatives(
            func_data['u1'],
            func_data['u2']
        )

        # 生成问题名称（用于模板头部显示）
        config['problem_name'] = f"{config['boundary_condition']}_{config['function_name']}_{config['domain']}"

        # 模板渲染：生成求解器脚本
        generator = TemplateGenerator()
        solver_script = generator.generate_solver(config)

        # 三层路径：问题类型/有限元空间/文件
        
        task_name = task_config['name']
        problem_dir = Path(output_dir) / task_name
        fespace_dir = problem_dir / task_config['fespace_name']
        fespace_dir.mkdir(parents=True, exist_ok=True)

        # 创建eps和png目录（平级）
        (fespace_dir / 'eps').mkdir(exist_ok=True)
        (fespace_dir / 'png').mkdir(exist_ok=True)

        # 写入文件
        for filename, content in solver_script.items():
            output_path = fespace_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return (True, "Generated")

    except Exception as e:
        return (False, str(e))


def main():
    parser = argparse.ArgumentParser(
        description='批量生成FreeFEM++脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--filter',
        type=str,
        help='过滤任务（如：Dirichlet, Electric, Magnetic）'
    )

    parser.add_argument(
        '--output',
        default='output',
        help='输出目录（默认：output）'
    )

    parser.add_argument(
        '--parallel',
        type=int,
        default=4,
        help='并行数（默认：4）'
    )

    args = parser.parse_args()

    # 生成所有任务
    all_tasks = generate_tasks()

    # 过滤任务（简单的子字符串匹配）
    if args.filter:
        tasks = [t for t in all_tasks if args.filter in f"{t['name']}/{t['fespace_name']}"]
        print(f"Filter: '{args.filter}' -> {len(tasks)}/{len(all_tasks)} tasks")
    else:
        tasks = all_tasks

    # 批量生成
    print("=" * 60)
    print(f"批量生成 {len(tasks)} 个FreeFEM++脚本")
    print(f"使用 {args.parallel} 个并行任务")
    print("=" * 60)

    success_count, fail_count, failed_tasks = parallel_map_with_progress(
        tasks,
        lambda task: generate_single_task(task, args.output),
        max_workers=args.parallel,
        item_name=lambda t: f"{t['name']}/{t['fespace_name']}"
    )

    # 总结
    print(f"\n{'=' * 60}")
    print(f"Generated: {success_count} succeeded, {fail_count} failed")
    print(f"{'=' * 60}")

    if success_count > 0:
        print(f"\nTo run the solvers:")
        print(f"  python scripts/run_freefem.py")

    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())