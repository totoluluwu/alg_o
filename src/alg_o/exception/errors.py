class AlgOError(Exception) :
    """Base exception for the alg_o library"""


class GenerationError(AlgOError) :
    """Base exception for data generation errors"""


class UnsupportedTypeError(GenerationError) :
    """Raised when a type is not supported by the generation module"""


class InvalidAnnotationError(GenerationError) :
    """Raised when a function annotation is invalid or malformed"""


class BenchmarkError(AlgOError) :
    """Raised when a benchmark process fails"""


class RegressionError(AlgOError) :
    """Raised when a regression process fails"""
