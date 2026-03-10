from abc import ABC, abstractmethod


class TypeSpec(ABC) :
    """Base class for resolved type specifications"""

    @property
    @abstractmethod
    def name( self ) -> str :
        """Readable type name"""


class DataGenerator(ABC) :
    """Base class for data generators"""

    @abstractmethod
    def generate( self, size: int ) -> object :
        """Generate a value for the requested size"""
