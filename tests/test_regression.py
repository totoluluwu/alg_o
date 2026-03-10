import pathlib
import sys
import time
import unittest
from dataclasses import FrozenInstanceError


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))

from alg_o import RegressionError, regression
from alg_o.regression import (
    ComplexityModel,
    ConstantModel,
    CubicModel,
    LinearModel,
    LinearithmicModel,
    LogarithmicModel,
    ModelFitResult,
    QuadraticModel,
    RegressionEngine,
    RegressionResult,
)


class DoubleModel(ComplexityModel) :

    @property
    def name( self ) -> str :
        return "Double"

    def evaluate( self, n: int ) -> float :
        return float(2 * n)


class ZeroModel(ComplexityModel) :

    @property
    def name( self ) -> str :
        return "Zero"

    def evaluate( self, n: int ) -> float :
        return 0.0


class RegressionModelsTests(unittest.TestCase) :

    def test_base_model_evaluate_all( self ) -> None :
        model = DoubleModel()
        self.assertEqual(model.evaluate_all([ 1, 2, 3 ]), [ 2.0, 4.0, 6.0 ])

    def test_constant_model( self ) -> None :
        model = ConstantModel()
        self.assertEqual(model.name, "O(1)")
        self.assertEqual(model.evaluate(100), 1.0)

    def test_logarithmic_model( self ) -> None :
        model = LogarithmicModel()
        self.assertEqual(model.name, "O(log n)")
        self.assertEqual(model.evaluate(1), 1.0)
        self.assertAlmostEqual(model.evaluate(8), 3.0)

    def test_linear_model( self ) -> None :
        model = LinearModel()
        self.assertEqual(model.name, "O(n)")
        self.assertEqual(model.evaluate(7), 7.0)

    def test_linearithmic_model( self ) -> None :
        model = LinearithmicModel()
        self.assertEqual(model.name, "O(n log n)")
        self.assertEqual(model.evaluate(1), 1.0)
        self.assertAlmostEqual(model.evaluate(8), 24.0)

    def test_quadratic_model( self ) -> None :
        model = QuadraticModel()
        self.assertEqual(model.name, "O(n^2)")
        self.assertEqual(model.evaluate(5), 25.0)

    def test_cubic_model( self ) -> None :
        model = CubicModel()
        self.assertEqual(model.name, "O(n^3)")
        self.assertEqual(model.evaluate(4), 64.0)


class RegressionResultTests(unittest.TestCase) :

    def test_result_get_fit( self ) -> None :
        fit_1 = ModelFitResult(
            model_name = "O(1)",
            coefficient = 1.0,
            error = 2.0,
            predicted_times = [ 1.0, 1.0 ],
        )
        fit_2 = ModelFitResult(
            model_name = "O(n)",
            coefficient = 0.5,
            error = 0.1,
            predicted_times = [ 0.5, 1.0 ],
        )
        result = RegressionResult(
            sizes = [ 1, 2 ],
            observed_times = [ 0.5, 1.0 ],
            model_fits = [ fit_1, fit_2 ],
            best_fit = fit_2,
        )

        self.assertIs(result.get_fit("O(n)"), fit_2)
        self.assertIsNone(result.get_fit("O(log n)"))

    def test_dataclasses_are_frozen( self ) -> None :
        fit = ModelFitResult(
            model_name = "O(1)",
            coefficient = 1.0,
            error = 0.0,
            predicted_times = [ 1.0 ],
        )
        with self.assertRaises(FrozenInstanceError) :
            fit.error = 1.0


class RegressionEngineTests(unittest.TestCase) :

    def test_default_models_are_loaded( self ) -> None :
        engine = RegressionEngine()
        names = [ model.name for model in engine._models ]
        self.assertEqual(
            names,
            [ "O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)" ],
        )

    def test_empty_model_list_raises( self ) -> None :
        with self.assertRaises(RegressionError) :
            RegressionEngine(models = [ ])

    def test_fit_linear_data_prefers_linear( self ) -> None :
        sizes = [ 1, 2, 4, 8, 16 ]
        times = [ 0.5, 1.0, 2.0, 4.0, 8.0 ]

        result = RegressionEngine().fit(sizes, times)
        linear_fit = result.get_fit("O(n)")

        self.assertEqual(result.best_fit.model_name, "O(n)")
        self.assertIsNotNone(linear_fit)
        assert linear_fit is not None
        self.assertAlmostEqual(linear_fit.coefficient, 0.5, places = 12)
        self.assertAlmostEqual(linear_fit.error, 0.0, places = 12)
        self.assertEqual(len(linear_fit.predicted_times), len(sizes))

    def test_fit_constant_data_prefers_constant( self ) -> None :
        sizes = [ 1, 2, 4, 8, 16 ]
        times = [ 3.0, 3.0, 3.0, 3.0, 3.0 ]

        result = RegressionEngine().fit(sizes, times)
        self.assertEqual(result.best_fit.model_name, "O(1)")

    def test_fit_with_custom_model( self ) -> None :
        engine = RegressionEngine(models = [ DoubleModel() ])
        result = engine.fit([ 1, 2, 3 ], [ 2.0, 4.0, 6.0 ])

        self.assertEqual(result.best_fit.model_name, "Double")
        self.assertAlmostEqual(result.best_fit.coefficient, 1.0, places = 12)
        self.assertAlmostEqual(result.best_fit.error, 0.0, places = 12)

    def test_fit_with_zero_model_keeps_zero_coefficient( self ) -> None :
        engine = RegressionEngine(models = [ ZeroModel() ])
        result = engine.fit([ 1, 2, 3 ], [ 1.0, 2.0, 3.0 ])

        self.assertEqual(result.best_fit.coefficient, 0.0)
        self.assertEqual(result.best_fit.predicted_times, [ 0.0, 0.0, 0.0 ])

    def test_validation_length_mismatch( self ) -> None :
        with self.assertRaisesRegex(RegressionError, "same length") :
            RegressionEngine().fit([ 1, 2 ], [ 1.0 ])

    def test_validation_empty_lists( self ) -> None :
        with self.assertRaisesRegex(RegressionError, "must not be empty") :
            RegressionEngine().fit([ ], [ ])

    def test_validation_non_positive_size( self ) -> None :
        with self.assertRaisesRegex(RegressionError, "strictly positive") :
            RegressionEngine().fit([ 0, 2 ], [ 1.0, 2.0 ])

    def test_validation_negative_time( self ) -> None :
        with self.assertRaisesRegex(RegressionError, "non-negative") :
            RegressionEngine().fit([ 1, 2 ], [ -1.0, 2.0 ])

    def test_edge_single_point_returns_first_model_on_tie( self ) -> None :
        result = RegressionEngine().fit([ 5 ], [ 10.0 ])
        self.assertEqual(result.best_fit.model_name, "O(1)")
        self.assertEqual(len(result.model_fits), 6)
        self.assertAlmostEqual(result.best_fit.error, 0.0, places = 12)

    def test_edge_all_zero_times( self ) -> None :
        sizes = [ 1, 2, 4, 8 ]
        times = [ 0.0, 0.0, 0.0, 0.0 ]

        result = RegressionEngine().fit(sizes, times)

        self.assertEqual(result.best_fit.model_name, "O(1)")
        for fit in result.model_fits :
            self.assertAlmostEqual(fit.coefficient, 0.0, places = 12)
            self.assertAlmostEqual(fit.error, 0.0, places = 12)
            self.assertEqual(fit.predicted_times, [ 0.0, 0.0, 0.0, 0.0 ])

    def test_edge_perfect_quadratic_data( self ) -> None :
        sizes = [ 1, 2, 3, 4 ]
        times = [ 0.25, 1.0, 2.25, 4.0 ]

        result = RegressionEngine().fit(sizes, times)
        quadratic_fit = result.get_fit("O(n^2)")

        self.assertEqual(result.best_fit.model_name, "O(n^2)")
        self.assertIsNotNone(quadratic_fit)
        assert quadratic_fit is not None
        self.assertAlmostEqual(quadratic_fit.coefficient, 0.25, places = 12)
        self.assertAlmostEqual(quadratic_fit.error, 0.0, places = 12)

    def test_edge_result_keeps_input_copies( self ) -> None :
        sizes = [ 1, 2, 3 ]
        times = [ 1.0, 2.0, 3.0 ]

        result = RegressionEngine().fit(sizes, times)
        sizes.append(4)
        times.append(4.0)

        self.assertEqual(result.sizes, [ 1, 2, 3 ])
        self.assertEqual(result.observed_times, [ 1.0, 2.0, 3.0 ])

    def test_edge_non_monotonic_times_still_returns_valid_result( self ) -> None :
        sizes = [ 1, 2, 3, 4, 5 ]
        times = [ 3.0, 1.0, 4.0, 1.5, 2.0 ]

        result = RegressionEngine().fit(sizes, times)

        self.assertEqual(result.sizes, sizes)
        self.assertEqual(result.observed_times, times)
        self.assertEqual(len(result.model_fits), 6)
        self.assertIn(result.best_fit, result.model_fits)


class RegressionPublicApiTests(unittest.TestCase) :

    def test_package_exports( self ) -> None :
        expected = {
            "ComplexityModel",
            "ConstantModel",
            "LogarithmicModel",
            "LinearModel",
            "LinearithmicModel",
            "QuadraticModel",
            "CubicModel",
            "RegressionEngine",
            "ModelFitResult",
            "RegressionResult",
        }
        self.assertEqual(set(regression.__all__), expected)

    def test_public_imports_work( self ) -> None :
        self.assertTrue(issubclass(LinearModel, ComplexityModel))
        self.assertIsInstance(RegressionEngine(), RegressionEngine)


class RegressionBenchmarkTests(unittest.TestCase) :

    def test_benchmark_many_small_fits( self ) -> None :
        engine = RegressionEngine()
        sizes = list(range(1, 201))
        times = [ size * 0.0002 for size in sizes ]
        iterations = 2000

        engine.fit(sizes, times)

        start = time.perf_counter()
        for _ in range(iterations) :
            engine.fit(sizes, times)
        elapsed = time.perf_counter() - start
        average_fit_time = elapsed / iterations

        self.assertLess(
            average_fit_time,
            0.01,
            msg = f"Average fit time too high: {average_fit_time:.6f}s",
        )

    def test_benchmark_one_large_fit( self ) -> None :
        engine = RegressionEngine()
        sizes = list(range(1, 10001))
        times = [ size * 0.00001 for size in sizes ]

        engine.fit(sizes, times)

        start = time.perf_counter()
        engine.fit(sizes, times)
        elapsed = time.perf_counter() - start

        self.assertLess(
            elapsed,
            0.5,
            msg = f"Single large fit too slow: {elapsed:.6f}s",
        )


if __name__ == "__main__" :
    unittest.main()
