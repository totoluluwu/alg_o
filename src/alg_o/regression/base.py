from abc import ABC, abstractmethod


class ComplexityModel(ABC) :
    """Base class for complexity models"""

    @property
    @abstractmethod
    def name( self ) -> str :
        """Readable model name"""

    @abstractmethod
    def evaluate( self, n: int ) -> float :
        """Evaluate the model for one input size"""

    def evaluate_all( self, sizes: list[ int ] ) -> list[ float ] :
        """Evaluate the model for many input sizes"""
        return [ self.evaluate(n) for n in sizes ]
