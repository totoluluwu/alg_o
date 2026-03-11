from dataclasses import dataclass


DEFAULT_BENCHMARK_SIZES: tuple[ int, ... ] = (10, 100, 500, 1000)
DEFAULT_BENCHMARK_REPEAT = 5
DEFAULT_BENCHMARK_WARMUP = 1


@dataclass(frozen = True)
class BenchmarkConfig :
    """Reusable benchmark configuration"""

    sizes: list[ int ]
    repeat: int = 5
    warmup: int = 1

    @classmethod
    def default( cls ) -> "BenchmarkConfig" :
        """Build a default benchmark configuration"""
        return cls(
            sizes = list(DEFAULT_BENCHMARK_SIZES),
            repeat = DEFAULT_BENCHMARK_REPEAT,
            warmup = DEFAULT_BENCHMARK_WARMUP,
        )
