#!/usr/bin/env python3
"""

使用Ghostscript进行图像转换（将EPS图像批量转换为PNG格式）

Usage:
    python scripts/convert_plots.py
    # 默认在当前目录下的'output'文件夹中查找并转换所有EPS为PNG
    python scripts/convert_plots.py --output project_data
    # 选择在'project_data' 目录内查找可转换文件
    python scripts/convert_plots.py --dpi 300
    # 将默认的150分辨率改为300分辨率
    python scripts/convert_plots.py --format pdf
    # 将默认的png转换格式更改为PDF
"""

import argparse
import subprocess
import platform
from pathlib import Path
from parallel_runner import parallel_map_with_progress
import sys

# Ghostscript设备映射（定义一次，全局使用）
DEVICE_MAP = {
    'png': 'png16m',
    'pdf': 'pdfwrite',
    'jpg': 'jpeg'
}

# 根据平台选择Ghostscript命令
GS_CMD = 'gswin64c' if platform.system() == 'Windows' else 'gs'

def convert_eps_to_format(eps_file, output_format='png', dpi=150):
    """使用Ghostscript转换EPS到其他格式"""
    # 路径: .../BDM1_P2/eps/error.eps → .../BDM1_P2/png/error.png
    output_dir = eps_file.parent.parent / output_format
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / eps_file.with_suffix(f'.{output_format}').name

    cmd = [
        GS_CMD,
        '-dSAFER', '-dBATCH', '-dNOPAUSE', '-dEPSCrop',
        f'-sDEVICE={DEVICE_MAP.get(output_format, "png16m")}',
        f'-r{dpi}',
        f'-sOutputFile={output_file}',
        str(eps_file)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if result.returncode == 0 and output_file.exists():
            return True, output_file
        else:
            return False, f"Conversion failed: {result.stderr.decode()[:100]}"

    except FileNotFoundError:
        return False, f"Ghostscript not found"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description='批量转换EPS图像到其他格式')
    parser.add_argument('--format', default='png', choices=['png', 'pdf', 'jpg'])
    parser.add_argument('--dpi', type=int, default=150, help='分辨率DPI (默认:150)')
    parser.add_argument('--output', default='output', help='输出目录')
    parser.add_argument('--parallel', type=int, default=4, help='并行数 (默认:4)')
    args = parser.parse_args()

    # 查找所有EPS文件
    eps_files = list(Path(args.output).glob('**/eps/*.eps'))
    if not eps_files:
        print(f"No EPS files found in {args.output}")
        return 1

    print(f"Found {len(eps_files)} EPS files")
    print(f"Converting to {args.format.upper()} at {args.dpi} DPI...")
    print(f"Using {args.parallel} parallel workers")
    print("=" * 60)

    # 并行转换
    success_count, fail_count, failed_files = parallel_map_with_progress(
        eps_files,
        lambda f: convert_eps_to_format(f, args.format, args.dpi),
        max_workers=args.parallel,
        item_name=lambda f: f.name
    )

    print("=" * 60)
    print(f"Summary: {success_count} succeeded, {fail_count} failed")
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())