import pathlib
import sys
import unittest
from dataclasses import FrozenInstanceError


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))

from alg_o import AlgOError, BenchmarkError, RegressionError
from alg_o.analysis import AnalysisResult, ComplexityEstimator
from alg_o.benchmark import BenchmarkPoint, BenchmarkResult
from alg_o.regression import ModelFitResult, RegressionResult


def _make_regression_result(
        best_model_name: str = "O(n)",
) -> RegressionResult :
    fit_1 = ModelFitResult(
        model_name = "O(1)",
        coefficient = 1.0,
        error = 2.0,
        predicted_times = [ 1.0, 1.0 ],
    )
    fit_2 = ModelFitResult(
        model_name = best_model_name,
        coefficient = 0.5,
        error = 0.1,
        predicted_times = [ 0.5, 1.0 ],
    )
    return RegressionResult(
        sizes = [ 1, 2 ],
        observed_times = [ 0.5, 1.0 ],
        model_fits = [ fit_1, fit_2 ],
        best_fit = fit_2,
    )


def _make_benchmark_result(
        function_name: str = "target",
) -> BenchmarkResult :
    return BenchmarkResult(
        function_name = function_name,
        points = [
            BenchmarkPoint(size = 1, times = [ 0.1, 0.2 ], average_time = 0.15),
            BenchmarkPoint(size = 2, times = [ 0.2, 0.4 ], average_time = 0.3),
        ],
    )


class StubBenchmarkRunner :

    def __init__(
            self,
            result: BenchmarkResult | None = None,
            error: Exception | None = None,
    ) -> None :
        self._result = result
        self._error = error
        self.called_with = None

    def run( self, func ) :
        self.called_with = func
        if self._error is not None :
            raise self._error
        assert self._result is not None
        return self._result


class StubRegressionEngine :

    def __init__(
            self,
            result: RegressionResult | None = None,
            error: Exception | None = None,
    ) -> None :
        self._result = result
        self._error = error
        self.called_with = None

    def fit( self, sizes, times ) :
        self.called_with = (sizes, times)
        if self._error is not None :
            raise self._error
        assert self._result is not None
        return self._result


class CallableWithoutName :

    def __call__( self, a: int ) -> None :
        _ = a


class AnalysisResultTests(unittest.TestCase) :

    def test_result_properties( self ) -> None :
        benchmark_result = _make_benchmark_result()
        regression_result = _make_regression_result(best_model_name = "O(n log n)")
        result = AnalysisResult(
            function_name = "target",
            benchmark_result = benchmark_result,
            regression_result = regression_result,
        )

        self.assertEqual(result.function_name, "target")
        self.assertEqual(result.best_complexity, "O(n log n)")
        self.assertEqual(result.sizes, [ 1, 2 ])
        self.assertEqual(result.times, [ 0.15, 0.3 ])

    def test_result_is_frozen( self ) -> None :
        result = AnalysisResult(
            function_name = "f",
            benchmark_result = _make_benchmark_result(),
            regression_result = _make_regression_result(),
        )
        with self.assertRaises(FrozenInstanceError) :
            result.function_name = "g"


class ComplexityEstimatorTests(unittest.TestCase) :

    def test_estimate_rejects_non_callable( self ) -> None :
        estimator = ComplexityEstimator()
        with self.assertRaisesRegex(AlgOError, "callable") :
            estimator.estimate(123)  # type: ignore[arg-type]

    def test_estimate_with_defaults( self ) -> None :
        estimator = ComplexityEstimator()

        def target( a: int ) -> None :
            _ = a

        result = estimator.estimate(target)

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.function_name, "target")
        self.assertEqual(len(result.sizes), 4)
        self.assertEqual(len(result.times), 4)
        self.assertIsInstance(result.best_complexity, str)

    def test_estimate_orchestrates_custom_dependencies( self ) -> None :
        benchmark_result = _make_benchmark_result(function_name = "from-benchmark")
        regression_result = _make_regression_result(best_model_name = "O(n^2)")
        benchmark_runner = StubBenchmarkRunner(result = benchmark_result)
        regression_engine = StubRegressionEngine(result = regression_result)
        estimator = ComplexityEstimator(
            benchmark_runner = benchmark_runner,
            regression_engine = regression_engine,
        )

        def target( a: int ) -> None :
            _ = a

        result = estimator.estimate(target)

        self.assertIs(benchmark_runner.called_with, target)
        self.assertEqual(
            regression_engine.called_with,
            (benchmark_result.sizes, benchmark_result.average_times),
        )
        self.assertIs(result.benchmark_result, benchmark_result)
        self.assertIs(result.regression_result, regression_result)
        self.assertEqual(result.function_name, "from-benchmark")
        self.assertEqual(result.best_complexity, "O(n^2)")

    def test_uses_function_name_fallback_if_benchmark_name_empty( self ) -> None :
        benchmark_runner = StubBenchmarkRunner(result = _make_benchmark_result(function_name = ""))
        regression_engine = StubRegressionEngine(result = _make_regression_result())
        estimator = ComplexityEstimator(
            benchmark_runner = benchmark_runner,
            regression_engine = regression_engine,
        )

        def target( a: int ) -> None :
            _ = a

        result = estimator.estimate(target)
        self.assertEqual(result.function_name, "target")

    def test_uses_callable_fallback_if_no_name( self ) -> None :
        benchmark_runner = StubBenchmarkRunner(result = _make_benchmark_result(function_name = ""))
        regression_engine = StubRegressionEngine(result = _make_regression_result())
        estimator = ComplexityEstimator(
            benchmark_runner = benchmark_runner,
            regression_engine = regression_engine,
        )

        result = estimator.estimate(CallableWithoutName())
        self.assertEqual(result.function_name, "<callable>")

    def test_benchmark_error_is_propagated( self ) -> None :
        benchmark_error = BenchmarkError("benchmark failed")
        estimator = ComplexityEstimator(
            benchmark_runner = StubBenchmarkRunner(error = benchmark_error),
            regression_engine = StubRegressionEngine(result = _make_regression_result()),
        )

        def target( a: int ) -> None :
            _ = a

        with self.assertRaises(BenchmarkError) as context :
            estimator.estimate(target)
        self.assertIs(context.exception, benchmark_error)

    def test_regression_error_is_propagated( self ) -> None :
        regression_error = RegressionError("regression failed")
        estimator = ComplexityEstimator(
            benchmark_runner = StubBenchmarkRunner(result = _make_benchmark_result()),
            regression_engine = StubRegressionEngine(error = regression_error),
        )

        def target( a: int ) -> None :
            _ = a

        with self.assertRaises(RegressionError) as context :
            estimator.estimate(target)
        self.assertIs(context.exception, regression_error)


class AnalysisPublicApiTests(unittest.TestCase) :

    def test_package_exports( self ) -> None :
        from alg_o import analysis

        expected = {
            "AnalysisResult",
            "ComplexityEstimator",
        }
        self.assertEqual(set(analysis.__all__), expected)

    def test_public_imports_work( self ) -> None :
        self.assertIsInstance(ComplexityEstimator(), ComplexityEstimator)


if __name__ == "__main__" :
    unittest.main()
