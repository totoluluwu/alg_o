import builtins
import pathlib
import sys
import unittest
from unittest.mock import MagicMock, patch


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))

from alg_o import AlgOError
from alg_o.analysis import AnalysisResult
from alg_o.benchmark import BenchmarkPoint, BenchmarkResult
from alg_o.plotting import ComplexityPlotter
from alg_o.regression import ModelFitResult, RegressionResult


def _make_benchmark_result() -> BenchmarkResult :
    return BenchmarkResult(
        function_name = "target",
        points = [
            BenchmarkPoint(size = 1, times = [ 0.1, 0.2 ], average_time = 0.15),
            BenchmarkPoint(size = 2, times = [ 0.2, 0.3 ], average_time = 0.25),
        ],
    )


def _make_regression_result() -> RegressionResult :
    fit_const = ModelFitResult(
        model_name = "O(1)",
        coefficient = 1.0,
        error = 0.2,
        predicted_times = [ 0.2, 0.2 ],
    )
    fit_linear = ModelFitResult(
        model_name = "O(n)",
        coefficient = 0.1,
        error = 0.1,
        predicted_times = [ 0.1, 0.2 ],
    )
    return RegressionResult(
        sizes = [ 1, 2 ],
        observed_times = [ 0.12, 0.24 ],
        model_fits = [ fit_const, fit_linear ],
        best_fit = fit_linear,
    )


def _make_analysis_result() -> AnalysisResult :
    return AnalysisResult(
        function_name = "target",
        benchmark_result = _make_benchmark_result(),
        regression_result = _make_regression_result(),
    )


class PlottingPublicApiTests(unittest.TestCase) :

    def test_package_exports( self ) -> None :
        from alg_o import plotting

        self.assertEqual(set(plotting.__all__), { "ComplexityPlotter" })

    def test_public_imports_work( self ) -> None :
        self.assertIsInstance(ComplexityPlotter(), ComplexityPlotter)


class PlottingBehaviorTests(unittest.TestCase) :

    def setUp( self ) -> None :
        self.plotter = ComplexityPlotter()
        self.pyplot = MagicMock()

    def test_plot_benchmark( self ) -> None :
        with patch.object(
                ComplexityPlotter,
                "_get_pyplot",
                return_value = self.pyplot,
        ) :
            self.plotter.plot_benchmark(_make_benchmark_result())

        self.pyplot.figure.assert_called_once()
        self.pyplot.plot.assert_called_once_with(
            [ 1, 2 ],
            [ 0.15, 0.25 ],
            marker = "o",
            label = "Measured",
        )
        self.pyplot.title.assert_called_once_with("Benchmark Results")
        self.pyplot.xlabel.assert_called_once_with("Input size")
        self.pyplot.ylabel.assert_called_once_with("Average execution time (s)")
        self.pyplot.grid.assert_called_once_with(True)
        self.pyplot.legend.assert_called_once()
        self.pyplot.show.assert_called_once()

    def test_plot_regression( self ) -> None :
        result = _make_regression_result()
        with patch.object(
                ComplexityPlotter,
                "_get_pyplot",
                return_value = self.pyplot,
        ) :
            self.plotter.plot_regression(result)

        self.pyplot.figure.assert_called_once()
        self.assertEqual(self.pyplot.plot.call_count, 2)
        first_call = self.pyplot.plot.call_args_list[ 0 ]
        second_call = self.pyplot.plot.call_args_list[ 1 ]
        self.assertEqual(first_call.args, ([ 1, 2 ], [ 0.12, 0.24 ]))
        self.assertEqual(first_call.kwargs, { "marker" : "o", "label" : "Observed" })
        self.assertEqual(second_call.args, ([ 1, 2 ], [ 0.1, 0.2 ]))
        self.assertEqual(
            second_call.kwargs,
            { "marker" : "x", "linestyle" : "--", "label" : "Predicted (O(n))" },
        )
        self.pyplot.title.assert_called_once_with("Regression Results - Best fit: O(n)")
        self.pyplot.xlabel.assert_called_once_with("Input size")
        self.pyplot.ylabel.assert_called_once_with("Execution time (s)")
        self.pyplot.grid.assert_called_once_with(True)
        self.pyplot.legend.assert_called_once()
        self.pyplot.show.assert_called_once()

    def test_plot_analysis( self ) -> None :
        result = _make_analysis_result()
        with patch.object(
                ComplexityPlotter,
                "_get_pyplot",
                return_value = self.pyplot,
        ) :
            self.plotter.plot_analysis(result)

        self.pyplot.figure.assert_called_once()
        self.assertEqual(self.pyplot.plot.call_count, 2)
        first_call = self.pyplot.plot.call_args_list[ 0 ]
        second_call = self.pyplot.plot.call_args_list[ 1 ]
        self.assertEqual(first_call.args, ([ 1, 2 ], [ 0.15, 0.25 ]))
        self.assertEqual(first_call.kwargs, { "marker" : "o", "label" : "Measured" })
        self.assertEqual(second_call.args, ([ 1, 2 ], [ 0.1, 0.2 ]))
        self.assertEqual(
            second_call.kwargs,
            { "marker" : "x", "linestyle" : "--", "label" : "Predicted" },
        )
        self.pyplot.title.assert_called_once_with(
            "target - inferred complexity: O(n)",
        )
        self.pyplot.xlabel.assert_called_once_with("Input size")
        self.pyplot.ylabel.assert_called_once_with("Execution time (s)")
        self.pyplot.grid.assert_called_once_with(True)
        self.pyplot.legend.assert_called_once()
        self.pyplot.show.assert_called_once()


class PlottingValidationTests(unittest.TestCase) :

    def setUp( self ) -> None :
        self.plotter = ComplexityPlotter()
        self.pyplot = MagicMock()

    def test_plot_benchmark_empty_data_raises( self ) -> None :
        empty_result = BenchmarkResult(function_name = "f", points = [ ])

        with patch.object(ComplexityPlotter, "_get_pyplot", return_value = self.pyplot) :
            with self.assertRaisesRegex(ValueError, "No data to plot for benchmark") :
                self.plotter.plot_benchmark(empty_result)

    def test_plot_regression_inconsistent_lengths_raise( self ) -> None :
        bad_fit = ModelFitResult(
            model_name = "O(n)",
            coefficient = 1.0,
            error = 0.0,
            predicted_times = [ 0.1 ],
        )
        bad_result = RegressionResult(
            sizes = [ 1, 2 ],
            observed_times = [ 0.1, 0.2 ],
            model_fits = [ bad_fit ],
            best_fit = bad_fit,
        )

        with patch.object(ComplexityPlotter, "_get_pyplot", return_value = self.pyplot) :
            with self.assertRaisesRegex(
                    ValueError,
                    "Inconsistent data lengths for regression predicted",
            ) :
                self.plotter.plot_regression(bad_result)

    def test_plot_analysis_inconsistent_lengths_raise( self ) -> None :
        benchmark_result = _make_benchmark_result()
        bad_fit = ModelFitResult(
            model_name = "O(n)",
            coefficient = 1.0,
            error = 0.0,
            predicted_times = [ 0.1 ],
        )
        bad_regression = RegressionResult(
            sizes = [ 1, 2 ],
            observed_times = [ 0.1, 0.2 ],
            model_fits = [ bad_fit ],
            best_fit = bad_fit,
        )
        bad_analysis = AnalysisResult(
            function_name = "f",
            benchmark_result = benchmark_result,
            regression_result = bad_regression,
        )

        with patch.object(ComplexityPlotter, "_get_pyplot", return_value = self.pyplot) :
            with self.assertRaisesRegex(
                    ValueError,
                    "Inconsistent data lengths for analysis predicted",
            ) :
                self.plotter.plot_analysis(bad_analysis)

    def test_get_pyplot_missing_matplotlib_raises_algo_error( self ) -> None :
        real_import = builtins.__import__

        def guarded_import( name, globals = None, locals = None, fromlist = (), level = 0 ) :
            if name == "matplotlib" or name.startswith("matplotlib.") :
                raise ModuleNotFoundError("matplotlib missing")
            return real_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect = guarded_import) :
            with self.assertRaisesRegex(
                    AlgOError, "matplotlib is required for plotting",
            ) as context :
                ComplexityPlotter._get_pyplot()

        self.assertIsInstance(context.exception.__cause__, ModuleNotFoundError)


if __name__ == "__main__" :
    unittest.main()
