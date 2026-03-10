# alg_o

`alg_o` is a Python library whose purpose is to empirically estimate the time complexity of user-defined functions.

The idea is to study how execution time evolves when the size of the input data increases.

The library is designed to:

- generate input data of different sizes,
- execute a user function on these generated structures,
- measure execution times,
- collect size/time observations,
- compare the observed growth with classical complexity models.

The goal is to provide an empirical approximation of temporal complexity based on measured data rather than theoretical analysis.

This project is intended as a tool for experimentation, algorithm analysis, and practical complexity observation.

## Installation

Install in editable mode for local development:

```bash
pip install -e .
```

Or install as a standard package:

```bash
pip install .
```

## Quick Start

```python
from alg_o.analysis import ComplexityEstimator
from alg_o.benchmark import BenchmarkConfig, BenchmarkRunner


def contains_zero(values: list[int]) -> bool:
    for value in values:
        if value == 0:
            return True
    return False


config = BenchmarkConfig(
    sizes=[100, 500, 1_000, 5_000],
    repeat=3,
    warmup=1,
)

estimator = ComplexityEstimator(
    benchmark_runner=BenchmarkRunner(config),
)

result = estimator.estimate(contains_zero)

print(result.function_name)   # contains_zero
print(result.best_complexity) # e.g. O(n)
print(result.sizes)           # benchmarked sizes
print(result.times)           # average times (seconds)
```

## Writing Analyzable Functions

`alg_o` uses function parameter annotations to generate inputs automatically.

Requirements:

- every function parameter must have a type annotation,
- supported annotation families are `int`, `float`, `str`, `list[T]`, and `dict[K, V]`,
- nested annotations are supported, for example `list[int]` and `dict[str, list[int]]`.

Example:

```python
def process(data: dict[str, list[int]]) -> int:
    return sum(sum(values) for values in data.values())
```

When benchmarking this function, the annotation `dict[str, list[int]]` drives input generation.

## Module Overview

- `alg_o.generation`: annotation resolution and argument generation (`TypeResolver`, `SignatureGenerator`, generators).
- `alg_o.benchmark`: runtime measurement over multiple sizes (`BenchmarkConfig`, `BenchmarkRunner`, `BenchmarkResult`).
- `alg_o.regression`: model fitting on measured data (`RegressionEngine`, `RegressionResult`, built-in complexity models).
- `alg_o.analysis`: high-level orchestration (`ComplexityEstimator`, `AnalysisResult`).
- `alg_o.plotting`: visualization utilities (`ComplexityPlotter`).
- `alg_o.config`: reusable configuration dataclasses (`BenchmarkConfig`, `EstimationConfig`).
- `alg_o.exception`: project-specific exception hierarchy (`AlgOError` and specialized errors).

## Main API

- `ComplexityEstimator` (`alg_o.analysis`): high-level orchestrator for full analysis (`benchmark -> regression`). Use this for standard end-to-end usage.
- `BenchmarkRunner` (`alg_o.benchmark`): runs timed executions on generated inputs for configured sizes. Use directly when you only need measurements.
- `RegressionEngine` (`alg_o.regression`): fits measured times against complexity models and returns fit errors. Use directly for custom time/size datasets.
- `SignatureGenerator` (`alg_o.generation`): resolves a function signature and generates arguments from annotations. Use directly to validate or inspect generation behavior.
- `ComplexityPlotter` (`alg_o.plotting`): plots benchmark and regression outputs (`plot_benchmark`, `plot_regression`, `plot_analysis`). Use when visualizing results.

Useful config object:

- `BenchmarkConfig` (`alg_o.benchmark` or `alg_o.config`): controls benchmark sizes, repeat count, and warmup count.

## Typical Workflow

- Define a typed user function.
- `SignatureGenerator` builds generators from parameter annotations.
- `BenchmarkRunner` runs the function over multiple input sizes and records timings.
- `RegressionEngine` fits timings against theoretical models.
- `ComplexityEstimator` returns the best inferred complexity.

Pipeline summary:

`user function -> generated inputs -> benchmark -> regression -> estimated complexity`

## Result Object

`ComplexityEstimator.estimate(...)` returns an `AnalysisResult` with:

- `function_name`: analyzed callable name,
- `benchmark_result`: full `BenchmarkResult` (raw points and averages),
- `regression_result`: full `RegressionResult` (all model fits and best fit),
- `best_complexity` (property): best model name,
- `sizes` (property): benchmarked input sizes,
- `times` (property): average execution time per size.

## Plotting

Use `ComplexityPlotter` to visualize benchmark and inference results.

```python
from alg_o.plotting import ComplexityPlotter


plotter = ComplexityPlotter()
plotter.plot_analysis(result)
```

Notes:

- `plot_analysis(result)` overlays measured times and best-fit predicted times.
- `plot_benchmark(benchmark_result)` and `plot_regression(regression_result)` are also available.
- `matplotlib` must be installed to use plotting.

## Available Complexity Models

The default regression engine compares:

- `O(1)`
- `O(log n)`
- `O(n)`
- `O(n log n)`
- `O(n^2)`
- `O(n^3)`

## Current Limitations

- Complexity estimation is empirical: it provides a best fit from measurements, not a formal proof.
- Function parameters must be annotated; missing annotations are rejected.
- Supported generated types are currently `int`, `float`, `str`, `list[T]`, and `dict[K, V]`.
- Dictionary key generation currently supports only `int`, `float`, and `str` key types.
