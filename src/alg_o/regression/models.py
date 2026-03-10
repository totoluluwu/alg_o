"""Built-in complexity model implementations"""

import math

from .base import ComplexityModel


class ConstantModel(ComplexityModel) :
    """O(1)"""

    @property
    def name( self ) -> str :
        return "O(1)"

    def evaluate( self, n: int ) -> float :
        # Constant value for any n
        return 1.0


class LogarithmicModel(ComplexityModel) :
    """O(log n)"""

    @property
    def name( self ) -> str :
        return "O(log n)"

    def evaluate( self, n: int ) -> float :
        # Clamp n to keep log defined and stable for small values
        return math.log2(max(2, n))


class LinearModel(ComplexityModel) :
    """O(n)"""

    @property
    def name( self ) -> str :
        return "O(n)"

    def evaluate( self, n: int ) -> float :
        return float(n)


class LinearithmicModel(ComplexityModel) :
    """O(n log n)"""

    @property
    def name( self ) -> str :
        return "O(n log n)"

    def evaluate( self, n: int ) -> float :
        return float(n) * math.log2(max(2, n))


class QuadraticModel(ComplexityModel) :
    """O(n^2)"""

    @property
    def name( self ) -> str :
        return "O(n^2)"

    def evaluate( self, n: int ) -> float :
        return float(n * n)


class CubicModel(ComplexityModel) :
    """O(n^3)"""

    @property
    def name( self ) -> str :
        return "O(n^3)"

    def evaluate( self, n: int ) -> float :
        return float(n * n * n)
