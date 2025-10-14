#!/usr/bin/env python3
"""
FreeFEM++ Pipeline - FreeFEM求解流水线

完整流程：
1. generate: 生成 FreeFEM++ 求解器脚本
2. solve:    运行求解器计算结果
3. convert:  转换 EPS 图像为 PNG/PDF

Usage:
    python pipeline.py                        # 完整流程，输出到 output/
    python pipeline.py --output workspace     # 输出目录改为 workspace/
    python pipeline.py --step generate        # 只生成求解脚本
    python pipeline.py --step solve           # 生成并求解（不转换图像）
    python pipeline.py --filter Dirichlet     # 只处理 Dirichlet 任务
    python pipeline.py --dpi 300              # 调整分辨率
    python pipeline.py --format pdf           # 转换为pdf格式
"""

import sys
import time
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, desc):
    """执行外部命令，返回是否成功。"""
    print(f"\n{'='*70}\n[{desc}]\n{'='*70}")

    start = time.time()
    try:
        subprocess.run(cmd, check=True)
        elapsed = time.time() - start
        print(f"\n{'='*70}")
        print(f"[OK] {desc} completed ({elapsed:.1f}s)")
        print(f"{'='*70}")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"\n{'='*70}")
        print(f"[FAIL] {desc} failed with exit code {e.returncode} ({elapsed:.1f}s)")
        print(f"{'='*70}")
        return False
    except FileNotFoundError:
        print(f"[FAIL] Command not found: {cmd[0]}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='FreeFEM++ Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--output', default='output',
                        help='Output directory (default: output)')
    parser.add_argument('--step', choices=['generate', 'solve', 'convert'], default='convert',
                        help='Execute until this step (default: convert)')
    parser.add_argument('--filter',
                        help='Task filter pattern (e.g., Dirichlet, Square)')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode: abort on any failure')
    parser.add_argument('--dpi', type=int, default=150,
                        help='Image DPI (default: 150)')
    parser.add_argument('--format', choices=['png', 'pdf', 'jpg'], default='png',
                        help='Image format (default: png)')

    args = parser.parse_args()

    # Print configuration
    print(f"\n{'='*70}")
    print(f"FreeFEM++ Pipeline")
    print(f"{'='*70}")
    print(f"Output: {args.output}")
    print(f"Steps:  generate → solve → convert (until: {args.step})")
    if args.filter:
        print(f"Filter: {args.filter}")
    if args.strict:
        print(f"Mode:   STRICT")

    start_time = time.time()

    # Step 1: Generate
    if args.step in ['generate', 'solve', 'convert']:
        cmd = [sys.executable, 'scripts/batch_generate.py', '--output', args.output]
        if args.filter:
            cmd.extend(['--filter', args.filter])

        if not run_command(cmd, 'Step 1/3: Generate solvers'):
            return 1

    # Step 2: Solve
    if args.step in ['solve', 'convert']:
        if not Path(args.output).exists():
            print(f"\n[FAIL] Directory '{args.output}' does not exist")
            print("  Run with --step generate first")
            return 1

        cmd = [sys.executable, 'scripts/run_freefem.py', '--output', args.output]

        if not run_command(cmd, 'Step 2/3: Solve'):
            return 1

    # Step 3: Convert
    if args.step == 'convert':
        eps_files = list(Path(args.output).glob('**/eps/*.eps'))

        if not eps_files:
            print(f"\n{'='*70}")
            print("[Step 3/3: Convert images]")
            print(f"{'='*70}")
            print("  No EPS files found, skipping")
        else:
            cmd = [sys.executable, 'scripts/convert_plots.py',
                   '--output', args.output,
                   '--dpi', str(args.dpi),
                   '--format', args.format]

            if not run_command(cmd, 'Step 3/3: Convert images'):
                if args.strict:
                    return 1
                print("  (continuing despite convert failure)")

    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"[SUCCESS] Pipeline completed in {elapsed:.1f}s")
    print(f"{'='*70}")
    print(f"\nResults in: {args.output}/")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[ABORT] Interrupted by user")
        sys.exit(1)
