import time
from typing import Callable

from ..exception import BenchmarkError
from ..generation import SignatureGenerator
from .config import BenchmarkConfig
from .result import BenchmarkPoint, BenchmarkResult


class BenchmarkRunner :
    """Run function benchmarks for configured input sizes"""

    def __init__( self, config: BenchmarkConfig | None = None ) -> None :
        """Create a benchmark runner"""
        if config is None :
            config = BenchmarkConfig(
                sizes = [ 10, 100, 500, 1000 ],
                repeat = 5,
                warmup = 1,
            )
        self._config = config

    def run( self, func: Callable[ ..., object ] ) -> BenchmarkResult :
        """Run benchmarks for one function"""
        if not callable(func) :
            raise BenchmarkError("func must be callable")

        function_name = getattr(func, "__name__", "<callable>")
        self._validate_config(self._config)
        signature_generator = self._build_signature_generator(func, function_name)

        points: list[ BenchmarkPoint ] = [ ]
        for size in self._config.sizes :
            points.append(self._benchmark_size(func, signature_generator, size))

        return BenchmarkResult(
            function_name = function_name,
            points = points,
        )

    @staticmethod
    def _validate_config( config: BenchmarkConfig ) -> None :
        """Validate benchmark configuration values"""
        if not config.sizes :
            raise BenchmarkError("sizes must not be empty")

        for size in config.sizes :
            if size <= 0 :
                raise BenchmarkError("all sizes must be strictly positive")

        if config.repeat <= 0 :
            raise BenchmarkError("repeat must be strictly positive")

        if config.warmup < 0 :
            raise BenchmarkError("warmup must be greater than or equal to zero")

    @staticmethod
    def _build_signature_generator(
            func: Callable[ ..., object ],
            function_name: str,
    ) -> SignatureGenerator :
        """Build the signature-driven argument generator"""
        try :
            return SignatureGenerator.from_function(func)
        except Exception as exc :
            raise BenchmarkError(
                f"failed to build signature generator for function '{function_name}'",
            ) from exc

    def _benchmark_size(
            self,
            func: Callable[ ..., object ],
            signature_generator: SignatureGenerator,
            size: int,
    ) -> BenchmarkPoint :
        """Benchmark one configured input size"""
        self._run_warmup(func, signature_generator, size, self._config.warmup)

        times: list[ float ] = [ ]
        for _ in range(self._config.repeat) :
            arguments = self._generate_arguments(signature_generator, size)
            times.append(self._measure_once(func, arguments, size))

        average_time = self._compute_average(times)
        return BenchmarkPoint(
            size = size,
            times = times,
            average_time = average_time,
        )

    @staticmethod
    def _generate_arguments(
            signature_generator: SignatureGenerator,
            size: int,
    ) -> dict[ str, object ] :
        """Generate benchmark arguments for one size"""
        try :
            return signature_generator.generate_arguments(size)
        except Exception as exc :
            raise BenchmarkError(f"failed to generate arguments for size {size}") from exc

    @staticmethod
    def _run_warmup(
            func: Callable[ ..., object ],
            signature_generator: SignatureGenerator,
            size: int,
            warmup: int,
    ) -> None :
        """Run warmup calls not counted in measured times"""
        for _ in range(warmup) :
            arguments = BenchmarkRunner._generate_arguments(signature_generator, size)
            try :
                func(**arguments)
            except Exception as exc :
                raise BenchmarkError(
                    f"function execution failed during warmup at size {size}",
                ) from exc

    @staticmethod
    def _measure_once(
            func: Callable[ ..., object ],
            arguments: dict[ str, object ],
            size: int,
    ) -> float :
        """Measure one function call duration in seconds"""
        start = time.perf_counter()
        try :
            func(**arguments)
        except Exception as exc :
            raise BenchmarkError(
                f"function execution failed during measurement at size {size}",
            ) from exc
        end = time.perf_counter()
        return end - start

    @staticmethod
    def _compute_average( times: list[ float ] ) -> float :
        """Compute arithmetic mean for measured times"""
        if not times :
            raise BenchmarkError("no measured times to average")
        return sum(times) / len(times)
