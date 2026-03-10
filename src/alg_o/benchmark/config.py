from dataclasses import dataclass


@dataclass(frozen = True)
class BenchmarkConfig :
    """Configuration for benchmark runs"""

    sizes: list[ int ]
    repeat: int = 5
    warmup: int = 1
