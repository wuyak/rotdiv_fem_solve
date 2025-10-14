#!/usr/bin/env python3
"""
运行FreeFEM++求解器脚本（批量执行solver.edp文件）

Usage:
    python scripts/run_freefem.py
    # 默认在'output'目录下运行所有solver.edp
    python scripts/run_freefem.py --output workspace
    # 指定输出目录为'workspace'
    python scripts/run_freefem.py --filter "Dirichlet*"
    # 仅运行匹配"Dirichlet*"模式的求解器
    python scripts/run_freefem.py --parallel 8
    # 使用8个并行工作进程（默认为4）
"""
import subprocess
import sys
import argparse
from pathlib import Path
from parallel_runner import parallel_map_with_progress


def run_solver(solver_path):
    """
    运行 FreeFEM solver

    Returns:
        (success: bool, message: str): 成功标志和结果消息
    """
    results_file = solver_path.parent / 'results.dat'

    try:
        # Delete old results
        if results_file.exists():
            results_file.unlink()

        # Run FreeFEM (-nw: no window mode)
        subprocess.run(
            ['FreeFem++', '-nw', 'solver.edp'],
            cwd=solver_path.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=600
        )

        # Check if results were generated
        if results_file.exists():
            return (True, "OK")
        else:
            return (False, "No results.dat generated")

    except subprocess.TimeoutExpired:
        return (False, "TIMEOUT (600s)")
    except Exception as e:
        return (False, str(e))


def main():
    parser = argparse.ArgumentParser(description='运行 FreeFEM++ solvers')
    parser.add_argument('--output', default='output', help='输出目录 (默认: output)')
    parser.add_argument('--filter', help='筛选 solver (支持通配符, 例如: "Dirichlet*")')
    parser.add_argument('--parallel', type=int, default=4, help='并行数 (默认: 4)')
    args = parser.parse_args()

    # 查找 solvers
    pattern = f'**/{args.filter or "*"}/solver.edp'
    solvers = list(Path(args.output).glob(pattern))

    if not solvers:
        print(f"No solvers found in {args.output}")
        return 1

    print(f"Found {len(solvers)} solvers")
    print(f"Using {args.parallel} parallel workers")
    print("=" * 60)

    # 并行运行
    success_count, fail_count, failed_solvers = parallel_map_with_progress(
        solvers,
        run_solver,
        max_workers=args.parallel,
        item_name=lambda s: str(s.parent.relative_to(args.output))
    )

    # Summary
    print("=" * 60)
    print(f"Summary: {success_count}/{len(solvers)} succeeded")

    if failed_solvers:
        print(f"\nFailed solvers ({fail_count}):")
        for solver in failed_solvers:
            name = solver.parent.relative_to(args.output)
            print(f"  - {name}")

    return 0 if success_count == len(solvers) else 1


if __name__ == '__main__':
    sys.exit(main())
