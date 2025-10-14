#!/usr/bin/env python3
"""
统一的并行任务执行接口，支持进度显示、错误处理和结果统计。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Tuple, Any


def parallel_map_with_progress(
    items: List[Any],
    worker: Callable[[Any], Tuple[bool, Any]],
    max_workers: int = 4,
    item_name: Callable[[Any], str] = str,
    timeout: int = None
) -> Tuple[int, int, List[Any]]:
    """
    并行执行任务并显示进度

    Args:
        items: 待处理的任务列表
        worker: 工作函数，接受单个item，返回 (success: bool, result_or_error: Any)
        max_workers: 最大并行工作进程数（默认: 4）
        item_name: 从item提取显示名称的函数（默认: str()）
        timeout: 可选的任务超时时间（秒）

    Returns:
        (success_count, fail_count, failed_items): 成功数、失败数、失败的任务列表

    Example:
        >>> def process_file(filepath):
        ...     try:
        ...         # 模拟文件处理
        ...         if not filepath.exists():
        ...             return (False, "File not found")
        ...         return (True, "Processed")
        ...     except Exception as e:
        ...         return (False, str(e))
        >>>
        >>> from pathlib import Path
        >>> files = [Path("data1.txt"), Path("missing.txt"), Path("data2.txt")]
        >>> success, fail, failed = parallel_map_with_progress(
        ...     files,
        ...     process_file,
        ...     max_workers=2,
        ...     item_name=lambda p: p.name
        ... )
        [1/3] [OK] data1.txt
        [2/3] [FAIL] missing.txt: File not found
        [3/3] [OK] data2.txt
        >>> success
        2
        >>> fail
        1
    """
    total = len(items)
    success_count = 0
    failed_items = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_item = {executor.submit(worker, item): item for item in items}

        # 按完成顺序处理结果
        for i, future in enumerate(as_completed(future_to_item), 1):
            item = future_to_item[future]
            name = item_name(item)

            try:
                # 获取结果（可选超时）
                success, result = future.result(timeout=timeout)

                if success:
                    print(f"[{i}/{total}] [OK] {name}")
                    success_count += 1
                else:
                    print(f"[{i}/{total}] [FAIL] {name}: {result}")
                    failed_items.append(item)

            except Exception as e:
                # 捕获所有异常（包括Timeout）
                error_type = type(e).__name__
                print(f"[{i}/{total}] [ERROR] {name}: {error_type}: {e}")
                failed_items.append(item)

    fail_count = len(failed_items)
    return success_count, fail_count, failed_items