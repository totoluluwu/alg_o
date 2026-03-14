from typing import Callable

from ..benchmark import BenchmarkRunner
from ..benchmark.result import BenchmarkResult
from ..exception import AlgOError
from ..regression import RegressionEngine
from .result import AnalysisResult


class ComplexityEstimator :
    """High-level orchestrator for benchmark and regression"""

    def __init__(
            self,
            benchmark_runner: BenchmarkRunner | None = None,
            regression_engine: RegressionEngine | None = None,
    ) -> None :
        """Create a complexity estimator"""
        if benchmark_runner is None :
            benchmark_runner = self._build_default_benchmark_runner()
        if regression_engine is None :
            regression_engine = self._build_default_regression_engine()

        self._benchmark_runner = benchmark_runner
        self._regression_engine = regression_engine

    def estimate( self, func: Callable[ ..., object ] ) -> AnalysisResult :
        """Run the full complexity estimation pipeline"""
        if not callable(func) :
            raise AlgOError("func must be callable")

        benchmark_result = self._benchmark_runner.run(func)
        regression_result = self._regression_engine.fit(
            benchmark_result.sizes,
            benchmark_result.average_times,
        )
        function_name = self._get_function_name(func, benchmark_result)

        return AnalysisResult(
            function_name = function_name,
            benchmark_result = benchmark_result,
            regression_result = regression_result,
        )

    @staticmethod
    def _build_default_benchmark_runner() -> BenchmarkRunner :
        """Build the default benchmark runner"""
        return BenchmarkRunner()

    @staticmethod
    def _build_default_regression_engine() -> RegressionEngine :
        """Build the default regression engine"""
        return RegressionEngine()

    @staticmethod
    def _get_function_name(
            func: Callable[ ..., object ],
            benchmark_result: BenchmarkResult,
    ) -> str :
        """Resolve function name for final analysis result"""
        if benchmark_result.function_name :
            return benchmark_result.function_name
        return getattr(func, "__name__", "<callable>")
