from dataclasses import dataclass


@dataclass(frozen = True)
class BenchmarkConfig :
    """Reusable benchmark configuration"""

    sizes: list[ int ]
    repeat: int = 5
    warmup: int = 1
