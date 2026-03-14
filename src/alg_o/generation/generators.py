import random
import string
from dataclasses import dataclass

from ..exception import GenerationError, UnsupportedTypeError
from .base import DataGenerator, TypeSpec
from .types import (
    DictTypeSpec,
    FloatTypeSpec,
    IntTypeSpec,
    ListTypeSpec,
    StringTypeSpec,
)


def _validate_size( size: int ) -> int :
    if size <= 0 :
        raise GenerationError("size must be strictly positive")
    return size


class IntGenerator(DataGenerator) :
    """Generate int values"""

    def generate( self, size: int ) -> int :
        current_size = _validate_size(size)
        return random.randint(-current_size, current_size)


class FloatGenerator(DataGenerator) :
    """Generate float values"""

    def generate( self, size: int ) -> float :
        current_size = _validate_size(size)
        return random.uniform(-float(current_size), float(current_size))


class StringGenerator(DataGenerator) :
    """Generate str values"""

    def generate( self, size: int ) -> str :
        current_size = _validate_size(size)
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(current_size))


@dataclass(frozen = True)
class ListGenerator(DataGenerator) :
    """Generate list values"""

    element_generator: DataGenerator

    def generate( self, size: int ) -> list[ object ] :
        current_size = _validate_size(size)
        child_size = max(1, current_size // 2)
        return [
            self.element_generator.generate(child_size)
            for _ in range(current_size)
        ]


@dataclass(frozen = True)
class DictGenerator(DataGenerator) :
    """Generate dict values"""

    key_generator: DataGenerator
    value_generator: DataGenerator

    def generate( self, size: int ) -> dict[ object, object ] :
        current_size = _validate_size(size)
        child_size = max(1, current_size // 2)

        data: dict[ object, object ] = { }
        max_attempts = max(10, current_size * 20)
        attempts = 0

        while len(data) < current_size :
            attempts += 1
            if attempts > max_attempts :
                raise GenerationError("Unable to generate enough unique dictionary keys")

            key = self.key_generator.generate(child_size)
            value = self.value_generator.generate(child_size)
            data[ key ] = value

        return data


def build_generator( type_spec: TypeSpec ) -> DataGenerator :
    """Build a data generator from a resolved type specification"""
    if isinstance(type_spec, IntTypeSpec) :
        return IntGenerator()

    if isinstance(type_spec, FloatTypeSpec) :
        return FloatGenerator()

    if isinstance(type_spec, StringTypeSpec) :
        return StringGenerator()

    if isinstance(type_spec, ListTypeSpec) :
        element_generator = build_generator(type_spec.element_type)
        return ListGenerator(element_generator = element_generator)

    if isinstance(type_spec, DictTypeSpec) :
        if not isinstance(type_spec.key_type, (IntTypeSpec, FloatTypeSpec, StringTypeSpec)) :
            raise UnsupportedTypeError(
                "Unsupported dictionary key type: only int, float and str are supported",
            )

        key_generator = build_generator(type_spec.key_type)
        value_generator = build_generator(type_spec.value_type)
        return DictGenerator(
            key_generator = key_generator,
            value_generator = value_generator,
        )

    raise UnsupportedTypeError(f"Unsupported type specification: {type_spec!r}")
