# 旋度-散度混合有限元求解器

自动化 FreeFEM++ 数值实验系统 —— 批量求解器生成与执行框架

---

## 环境要求

### 必需软件

- **FreeFEM++ 4.0+** —— 有限元求解器
- **Python 3.8+** —— 流程管理

### Python 依赖

```bash
pip install -r requirements.txt
```

**requirements.txt**：
```txt
jinja2>=3.1.0    # 模板引擎
sympy>=1.12      # 符号计算
```

### 可选软件

- **Ghostscript** —— EPS → PNG/PDF 图像格式转换

---

## 快速开始

```bash
python pipeline.py    # 生成 → 求解 → 转换
```

> 图像转换步骤需要 Ghostscript。若未安装，可执行：

```bash
python pipeline.py --step solve    # 生成 → 求解
```

**执行示例**：
```text
批量生成 24 个 FreeFEM++ 脚本
使用 4 个并行任务
[1/24] [OK] Dirichlet_Trig_Square/BDM1_P2
...
[24/24] [OK] Magnetic_Trig_Lshaped/BDM2Ortho_P3

Generated: 24 succeeded, 0 failed
Summary: 24/24 succeeded

[SUCCESS] Pipeline completed in 20.3s
```

---

## 项目定位

### FreeFEM++ 的核心功能

FreeFEM++ 在二维混合有限元求解方面具有成熟的网格生成能力和丰富的函数空间支持，可以稳定高效地处理复杂的偏微分方程组。负责有限元离散化、线性系统求解和数值结果输出。

### 数值实验的其他环节

进行大规模数值实验时，除了求解器本身，还需要：

1. **符号计算** —— 从给定的精确解推导偏导数、散度、旋度和源项表达式，用于误差验证
2. **批量代码生成** —— 针对多参数组合（边界条件 × 计算域 × 有限元空间）自动生成求解器脚本
3. **图像格式转换** —— 将 FreeFEM++ 输出的 EPS 格式转换为 PNG 格式

### 本项目的作用

本项目为 FreeFEM++ 补充前处理和后处理功能：

**工作流程**：
1. **SymPy 符号推导** —— 给定精确解，自动推导偏导数、散度、旋度和源项
2. **Jinja2 模板引擎** —— 将配置参数注入 FreeFEM++ 脚本模板，批量生成求解器
3. **Python 流程管理** —— 协调生成、求解和数值结果存储，支持多核并行
4. **Ghostscript 图像转换** —— 批量转换 EPS 图像为 PNG 格式

**拓展实验**：新增实验仅需在函数库中定义测试函数配置，系统自动完成脚本生成、求解和结果分析全流程

---

## 项目结构

```
rot_div_refactor/
├── pipeline.py                       # 主入口，协调三个执行阶段
├── requirements.txt                  # Python 依赖清单
├── scripts/                          # Python 模块
│   ├── batch_generate.py             # 批量生成求解器脚本
│   ├── run_freefem.py                # FreeFEM++ 并行求解
│   ├── convert_plots.py              # Ghostscript 图像转换
│   ├── template_generator.py         # Jinja2 模板渲染引擎
│   ├── symbolic_derivatives.py       # SymPy 符号计算
│   ├── function_library.py           # 测试函数配置库
│   └── parallel_runner.py            # 并行框架
├── templates/                        # Jinja2 模板
│   ├── solver.edp.j2                 # FreeFEM++ 主求解器模板
│   └── includes/                     # 子模板（网格、误差、输出、绘图）
│       ├── arrays.idp.j2
│       ├── mesh.idp.j2
│       ├── errors.idp.j2
│       ├── output.idp.j2
│       └── plot.idp.j2
└── output/                           # 输出目录
```

**核心文件说明**：
- `function_library.py` —— 测试函数配置库（新增测试函数）
- `batch_generate.py` —— FreeFEM++ 脚本生成器
- `pipeline.py` —— 主入口和流程控制
- `templates/solver.edp.j2` —— FreeFEM++ 求解脚本主模版
- `templates/includes/*.idp.j2` —— 子模板（网格生成、误差计算、结果输出、图像绘制）

---

## 使用方法

### 执行完整流程

```bash
python pipeline.py                  # 生成 + 求解 + 转换
python pipeline.py --step generate  # 仅生成脚本
python pipeline.py --step solve     # 生成 + 求解（不转换图像）
```

### 筛选配置

```bash
python pipeline.py --filter Dirichlet_Trig_Square    # 组合筛选
python pipeline.py --filter BDM2                     # 所有 BDM2 空间
```

### 输出控制

```bash
python pipeline.py --output workspace    # 指定输出目录
python pipeline.py --dpi 300             # 高分辨率图像
```

### 输出结构

```
output/
└── {BoundaryCondition}_{Function}_{Domain}/
    └── {FESpace}_{LagrangeSpace}/
        ├── solver.edp           # FreeFEM++ 求解器
        ├── results.dat          # 数值解数据
        ├── summary.txt          # 收敛率报告
        └── eps/
            ├── *.eps            # 原始图像
            └── png/
                └── *.png        # 转换后图像
```

### 输出示例

**收敛率分析报告** (`summary.txt`)：
```
========================================
Convergence Analysis Report
========================================
Problem: Dirichlet_Trigonometric_Square
Finite Element: BDM1 + P2
Mesh refinements: 4
========================================

========================================
H1 Error of u
========================================
Mesh    Error          Rate
----------------------------------------
  0     1.234e-01   -
  1     3.089e-02   2.00
  2     7.721e-03   2.00
  3     1.930e-03   2.00
```

---

## 扩展

### 添加测试函数

编辑 `scripts/function_library.py`：

```python
FUNCTION_LIBRARY = {
    'Dirichlet': {
        'MyFunction': {
            'u1': 'x**2 * (1-x)**2 * y',
            'u2': '-x * y**2 * (1-y)**2',
            'domain': ['Square']
        }
    }
}
```

然后运行：
```bash
python pipeline.py --filter MyFunction
```

### 添加有限元空间

编辑 `scripts/batch_generate.py` 中的 `FESPACE_COMBINATIONS`：

```python
FESPACE_COMBINATIONS = {
    'Dirichlet': [
        ('BDM1', 'P2'),
        ('BDM2', 'P3'),
        ('RT2', 'P2'),    # 新增 Raviart-Thomas 空间
    ],
}
```

### 自定义网格细化

修改生成的 `solver.edp` 文件或传递 FreeFEM++ 参数：

```bash
FreeFem++ solver.edp -nref 5    # 5 次自适应细化
```