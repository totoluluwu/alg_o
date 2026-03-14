import inspect
from dataclasses import dataclass
from typing import Callable

from ..exception import GenerationError, InvalidAnnotationError
from .base import DataGenerator, TypeSpec
from .generators import build_generator
from .resolver import TypeResolver


@dataclass(frozen = True)
class ParameterSpec :
    """Resolved specification for one function parameter"""

    name: str
    type_spec: TypeSpec


class SignatureGenerator :
    """Inspect function signatures and generate argument values"""

    def __init__(
            self,
            parameters: list[ ParameterSpec ],
            generators: dict[ str, DataGenerator ],
    ) -> None :
        """Create a signature generator from resolved parameters"""
        self._parameters = list(parameters)
        self._generators = dict(generators)

    @classmethod
    def from_function( cls, func: Callable[ ..., object ] ) -> "SignatureGenerator" :
        """Build a signature generator from a user function"""
        signature = inspect.signature(func)
        resolver = TypeResolver()

        parameters: list[ ParameterSpec ] = [ ]
        generators: dict[ str, DataGenerator ] = { }

        for parameter in signature.parameters.values() :
            if parameter.annotation is inspect._empty :
                raise InvalidAnnotationError(
                    f"Parameter '{parameter.name}' has no type annotation",
                )

            type_spec = resolver.resolve(parameter.annotation)
            parameters.append(ParameterSpec(name = parameter.name, type_spec = type_spec))
            generators[ parameter.name ] = build_generator(type_spec)

        return cls(parameters = parameters, generators = generators)

    @property
    def parameters( self ) -> list[ ParameterSpec ] :
        """Return resolved parameter specifications"""
        return list(self._parameters)

    def generate_arguments( self, size: int ) -> dict[ str, object ] :
        """Generate one argument value per parameter"""
        if size <= 0 :
            raise GenerationError("size must be strictly positive")

        arguments: dict[ str, object ] = { }
        for parameter in self._parameters :
            generator = self._generators[ parameter.name ]
            arguments[ parameter.name ] = generator.generate(size)
        return arguments
