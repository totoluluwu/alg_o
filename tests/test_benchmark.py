import pathlib
import sys
import unittest
from dataclasses import FrozenInstanceError


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))

from alg_o import BenchmarkError, GenerationError, InvalidAnnotationError
from alg_o.benchmark import (
    BenchmarkConfig,
    BenchmarkPoint,
    BenchmarkResult,
    BenchmarkRunner,
)
from alg_o.benchmark.runner import BenchmarkRunner as BenchmarkRunnerImpl


class FailingSignatureGenerator :

    def generate_arguments( self, size: int ) -> dict[ str, object ] :
        raise GenerationError(f"boom for size {size}")


class CallableWithoutName :

    def __call__( self, a: int ) -> None :
        _ = a


class BenchmarkConfigTests(unittest.TestCase) :

    def test_defaults( self ) -> None :
        config = BenchmarkConfig(sizes = [ 1, 2, 3 ])
        self.assertEqual(config.sizes, [ 1, 2, 3 ])
        self.assertEqual(config.repeat, 5)
        self.assertEqual(config.warmup, 1)

    def test_config_is_frozen( self ) -> None :
        config = BenchmarkConfig(sizes = [ 1 ])
        with self.assertRaises(FrozenInstanceError) :
            config.repeat = 10


class BenchmarkResultTests(unittest.TestCase) :

    def test_result_properties( self ) -> None :
        points = [
            BenchmarkPoint(size = 2, times = [ 0.1, 0.2 ], average_time = 0.15),
            BenchmarkPoint(size = 4, times = [ 0.4, 0.6 ], average_time = 0.5),
        ]
        result = BenchmarkResult(function_name = "f", points = points)

        self.assertEqual(result.sizes, [ 2, 4 ])
        self.assertEqual(result.average_times, [ 0.15, 0.5 ])

    def test_result_and_point_are_frozen( self ) -> None :
        point = BenchmarkPoint(size = 1, times = [ 0.1 ], average_time = 0.1)
        result = BenchmarkResult(function_name = "f", points = [ point ])

        with self.assertRaises(FrozenInstanceError) :
            point.average_time = 1.0
        with self.assertRaises(FrozenInstanceError) :
            result.function_name = "g"


class BenchmarkRunnerValidationTests(unittest.TestCase) :

    def test_run_rejects_non_callable( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 1 ], repeat = 1, warmup = 0))
        with self.assertRaisesRegex(BenchmarkError, "callable") :
            runner.run(123)  # type: ignore[arg-type]

    def test_empty_sizes_raises( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ ], repeat = 1, warmup = 0))

        def target( a: int ) -> None :
            _ = a

        with self.assertRaisesRegex(BenchmarkError, "sizes must not be empty") :
            runner.run(target)

    def test_non_positive_size_raises( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 1, 0 ], repeat = 1, warmup = 0))

        def target( a: int ) -> None :
            _ = a

        with self.assertRaisesRegex(BenchmarkError, "strictly positive") :
            runner.run(target)

    def test_repeat_must_be_positive( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 1 ], repeat = 0, warmup = 0))

        def target( a: int ) -> None :
            _ = a

        with self.assertRaisesRegex(BenchmarkError, "repeat") :
            runner.run(target)

    def test_warmup_must_be_non_negative( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 1 ], repeat = 1, warmup = -1))

        def target( a: int ) -> None :
            _ = a

        with self.assertRaisesRegex(BenchmarkError, "warmup") :
            runner.run(target)


class BenchmarkRunnerBehaviorTests(unittest.TestCase) :

    def test_run_with_default_config( self ) -> None :
        runner = BenchmarkRunner()

        def target( a: int ) -> None :
            _ = a

        result = runner.run(target)

        self.assertEqual(result.function_name, "target")
        self.assertEqual(result.sizes, [ 10, 100, 500, 1000 ])
        self.assertEqual(len(result.points), 4)
        for point in result.points :
            self.assertEqual(len(point.times), 5)
            self.assertGreaterEqual(point.average_time, 0.0)

    def test_run_preserves_size_order( self ) -> None :
        config = BenchmarkConfig(sizes = [ 7, 1, 3 ], repeat = 1, warmup = 0)
        runner = BenchmarkRunner(config)

        def target( a: int ) -> None :
            _ = a

        result = runner.run(target)
        self.assertEqual(result.sizes, [ 7, 1, 3 ])

    def test_callable_without_name_uses_fallback( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 1 ], repeat = 1, warmup = 0))
        result = runner.run(CallableWithoutName())
        self.assertEqual(result.function_name, "<callable>")

    def test_signature_generation_failure_is_wrapped( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 1 ], repeat = 1, warmup = 0))

        def target( a ) -> None :  # missing annotation by design
            _ = a

        with self.assertRaisesRegex(
                BenchmarkError,
                "failed to build signature generator for function 'target'",
        ) as context :
            runner.run(target)

        self.assertIsInstance(context.exception.__cause__, InvalidAnnotationError)

    def test_generate_arguments_failure_is_wrapped_with_size( self ) -> None :
        with self.assertRaisesRegex(
                BenchmarkError,
                "failed to generate arguments for size 9",
        ) as context :
            BenchmarkRunnerImpl._generate_arguments(FailingSignatureGenerator(), 9)

        self.assertIsInstance(context.exception.__cause__, GenerationError)

    def test_warmup_failure_is_wrapped_with_size( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 2 ], repeat = 1, warmup = 1))

        def target( a: int ) -> None :
            _ = a
            raise RuntimeError("fail in warmup")

        with self.assertRaisesRegex(
                BenchmarkError,
                "warmup at size 2",
        ) as context :
            runner.run(target)

        self.assertIsInstance(context.exception.__cause__, RuntimeError)

    def test_measurement_failure_is_wrapped_with_size( self ) -> None :
        runner = BenchmarkRunner(BenchmarkConfig(sizes = [ 3 ], repeat = 1, warmup = 0))

        def target( a: int ) -> None :
            _ = a
            raise RuntimeError("fail in measure")

        with self.assertRaisesRegex(
                BenchmarkError,
                "measurement at size 3",
        ) as context :
            runner.run(target)

        self.assertIsInstance(context.exception.__cause__, RuntimeError)

    def test_compute_average_empty_raises( self ) -> None :
        with self.assertRaisesRegex(BenchmarkError, "no measured times") :
            BenchmarkRunnerImpl._compute_average([ ])

    def test_compute_average_non_empty( self ) -> None :
        value = BenchmarkRunnerImpl._compute_average([ 1.0, 2.0, 3.0 ])
        self.assertEqual(value, 2.0)


class BenchmarkRunnerFreshInputTests(unittest.TestCase) :

    def test_warmup_and_measurement_use_fresh_arguments( self ) -> None :
        seen_inputs: list[ list[ int ] ] = [ ]

        def target( values: list[ int ] ) -> None :
            seen_inputs.append(values)
            values.pop()
            values.pop()

        config = BenchmarkConfig(sizes = [ 2 ], repeat = 3, warmup = 2)
        result = BenchmarkRunner(config).run(target)

        self.assertEqual(result.sizes, [ 2 ])
        self.assertEqual(len(result.points[ 0 ].times), 3)
        self.assertEqual(len(seen_inputs), 5)
        self.assertEqual(len({ id(value) for value in seen_inputs }), 5)

    def test_warmup_runs_are_not_counted( self ) -> None :
        call_count = { "total" : 0 }

        def target( a: int ) -> None :
            _ = a
            call_count[ "total" ] += 1

        config = BenchmarkConfig(sizes = [ 4 ], repeat = 4, warmup = 3)
        result = BenchmarkRunner(config).run(target)

        self.assertEqual(call_count[ "total" ], 7)
        self.assertEqual(len(result.points[ 0 ].times), 4)


class BenchmarkPublicApiTests(unittest.TestCase) :

    def test_package_exports( self ) -> None :
        from alg_o import benchmark

        expected = {
            "BenchmarkConfig",
            "BenchmarkPoint",
            "BenchmarkResult",
            "BenchmarkRunner",
        }
        self.assertEqual(set(benchmark.__all__), expected)

    def test_public_imports_work( self ) -> None :
        self.assertIsInstance(BenchmarkRunner(), BenchmarkRunner)
        self.assertIsInstance(
            BenchmarkConfig(sizes = [ 1 ]),
            BenchmarkConfig,
        )


if __name__ == "__main__" :
    unittest.main()
