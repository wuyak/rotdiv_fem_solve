<p style="text-align: center;">
    Curl-Div Mixed Finite Element Solver<br>
    Automated FreeFEM++ Numerical Experiment System — Batch Solver Generation and Execution Framework
</p>

<p style="text-align: center;">
    English · [<a href="./README_zh_CN.md">中文</a>]
</p>

---

## 📋 Requirements

### Required Software

- **FreeFEM++ 4.0+** — Finite element solver
- **Python 3.8+** — Workflow management

### Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```txt
jinja2>=3.1.0    # Template engine
sympy>=1.12      # Symbolic computation
```

### Optional Software

- **Ghostscript** — EPS → PNG/PDF image format conversion

---

## 🚀 Quick Start

```bash
python pipeline.py    # Generate → Solve → Convert
```

> 💡 Image conversion requires Ghostscript. If not installed, run:

```bash
python pipeline.py --step solve    # Generate → Solve
```

**Execution Example**:
```text
Batch generating 24 FreeFEM++ scripts
Using 4 parallel tasks
[1/24] [OK] Dirichlet_Trig_Square/BDM1_P2
...
[24/24] [OK] Magnetic_Trig_Lshaped/BDM2Ortho_P3

Generated: 24 succeeded, 0 failed
Summary: 24/24 succeeded

[SUCCESS] Pipeline completed in 20.3s
```

---

## 📍 Project Overview

### FreeFEM++ Core Functionality

FreeFEM++ excels in 2D mixed finite element solving with mature mesh generation capabilities and rich function space support, efficiently handling complex PDE systems. It handles finite element discretization, linear system solving, and numerical result output.

### Other Aspects of Numerical Experiments

Large-scale numerical experiments require more than just the solver:

1. **Symbolic computation** — Derive partial derivatives, divergence, curl, and source terms from exact solutions for error verification
2. **Batch code generation** — Automatically generate solver scripts for parameter combinations (boundary conditions × domains × finite element spaces)
3. **Image format conversion** — Convert FreeFEM++ EPS output to PNG format

### Purpose of This Project

This project provides pre-processing and post-processing for FreeFEM++:

**Workflow**:
1. **SymPy symbolic derivation** — Given exact solutions, automatically derive derivatives, divergence, curl, and source terms
2. **Jinja2 template engine** — Inject configuration parameters into FreeFEM++ script templates for batch solver generation
3. **Python workflow management** — Coordinate generation, solving, and result storage with multi-core parallelism
4. **Ghostscript image conversion** — Batch convert EPS images to PNG format

**Experiment Extension**: Adding new experiments only requires defining test function configurations in the function library; the system automatically handles script generation, solving, and result analysis

---

## 📁 Project Structure

```
rot_div_refactor/
├── pipeline.py                       # Main entry, coordinates three execution stages
├── requirements.txt                  # Python dependency list
├── scripts/                          # Python modules
│   ├── batch_generate.py             # Batch solver script generation
│   ├── run_freefem.py                # FreeFEM++ parallel solving
│   ├── convert_plots.py              # Ghostscript image conversion
│   ├── template_generator.py         # Jinja2 template rendering engine
│   ├── symbolic_derivatives.py       # SymPy symbolic computation
│   ├── function_library.py           # Test function configuration library
│   └── parallel_runner.py            # Parallel framework
├── templates/                        # Jinja2 templates
│   ├── solver.edp.j2                 # FreeFEM++ main solver template
│   └── includes/                     # Sub-templates (mesh, error, output, plot)
│       ├── arrays.idp.j2
│       ├── mesh.idp.j2
│       ├── errors.idp.j2
│       ├── output.idp.j2
│       └── plot.idp.j2
└── output/                           # Output directory
```

**Core File Descriptions**:
- `function_library.py` — Test function configuration library (add new test functions)
- `batch_generate.py` — FreeFEM++ script generator
- `pipeline.py` — Main entry and workflow control
- `templates/solver.edp.j2` — FreeFEM++ solver script main template
- `templates/includes/*.idp.j2` — Sub-templates (mesh generation, error calculation, result output, plotting)

---

## 💻 Usage

### Execute Complete Workflow

```bash
python pipeline.py                  # Generate + Solve + Convert
python pipeline.py --step generate  # Generate scripts only
python pipeline.py --step solve     # Generate + Solve (no image conversion)
```

### Filter Configurations

```bash
python pipeline.py --filter Dirichlet_Trig_Square    # Combination filter
python pipeline.py --filter BDM2                     # All BDM2 spaces
```

### Output Control

```bash
python pipeline.py --output workspace    # Specify output directory
python pipeline.py --dpi 300             # High-resolution images
```

### Output Structure

```
output/
└── {BoundaryCondition}_{Function}_{Domain}/
    └── {FESpace}_{LagrangeSpace}/
        ├── solver.edp           # FreeFEM++ solver
        ├── results.dat          # Numerical solution data
        ├── summary.txt          # Convergence rate report
        └── eps/
            ├── *.eps            # Original images
            └── png/
                └── *.png        # Converted images
```

### Output Example

**Convergence Rate Analysis Report** (`summary.txt`):
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

## 🔧 Extensions

### Add Test Functions

Edit `scripts/function_library.py`:

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

Then run:
```bash
python pipeline.py --filter MyFunction
```

### Add Finite Element Spaces

Edit `FESPACE_COMBINATIONS` in `scripts/batch_generate.py`:

```python
FESPACE_COMBINATIONS = {
    'Dirichlet': [
        ('BDM1', 'P2'),
        ('BDM2', 'P3'),
        ('RT2', 'P2'),    # Add Raviart-Thomas space
    ],
}
```

### Custom Mesh Refinement

Modify the generated `solver.edp` file or pass FreeFEM++ parameters:

```bash
FreeFem++ solver.edp -nref 5    # 5 adaptive refinements
```

---