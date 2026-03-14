from dataclasses import dataclass

from ..benchmark import BenchmarkResult
from ..regression import RegressionResult


@dataclass(frozen = True)
class AnalysisResult :
    """Final analysis output for one function"""

    function_name: str
    benchmark_result: BenchmarkResult
    regression_result: RegressionResult

    @property
    def best_complexity( self ) -> str :
        """Return the best fitted complexity model name"""
        return self.regression_result.best_fit.model_name

    @property
    def sizes( self ) -> list[ int ] :
        """Return benchmarked input sizes"""
        return self.benchmark_result.sizes

    @property
    def times( self ) -> list[ float ] :
        """Return average benchmark times"""
        return self.benchmark_result.average_times
