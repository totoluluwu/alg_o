from dataclasses import dataclass


@dataclass(frozen = True)
class BenchmarkPoint :
    """Benchmark measurements for one input size"""

    size: int
    times: list[ float ]
    average_time: float


@dataclass(frozen = True)
class BenchmarkResult :
    """Full benchmark result for one function"""

    function_name: str
    points: list[ BenchmarkPoint ]

    @property
    def sizes( self ) -> list[ int ] :
        """Return benchmarked input sizes"""
        return [ point.size for point in self.points ]

    @property
    def average_times( self ) -> list[ float ] :
        """Return average measured times by size"""
        return [ point.average_time for point in self.points ]
