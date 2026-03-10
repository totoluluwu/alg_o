from dataclasses import dataclass

from .benchmark import BenchmarkConfig


@dataclass(frozen = True)
class EstimationConfig :
    """Reusable top-level configuration for complexity estimation"""

    benchmark: BenchmarkConfig

    @classmethod
    def default( cls ) -> "EstimationConfig" :
        """Build a default estimation configuration"""
        return cls(
            benchmark = BenchmarkConfig(
                sizes = [ 10, 100, 500, 1000 ],
                repeat = 5,
                warmup = 1,
            ),
        )
