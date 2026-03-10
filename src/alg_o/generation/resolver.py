from typing import get_args, get_origin

from .base import TypeSpec
from .types import (
    DictTypeSpec,
    FloatTypeSpec,
    IntTypeSpec,
    ListTypeSpec,
    StringTypeSpec,
)


class TypeResolver :
    """Resolve Python annotations into TypeSpec objects"""

    def resolve( self, annotation: object ) -> TypeSpec :
        """Resolve one annotation"""
        if annotation is int :
            return IntTypeSpec()

        if annotation is float :
            return FloatTypeSpec()

        if annotation is str :
            return StringTypeSpec()

        if annotation is list :
            raise ValueError("Malformed list annotation: expected list[T]")

        if annotation is dict :
            raise ValueError("Malformed dict annotation: expected dict[K, V]")

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is list :
            if len(args) != 1 :
                raise ValueError("Malformed list annotation: expected list[T]")

            element_type = self.resolve(args[ 0 ])
            return ListTypeSpec(element_type = element_type)

        if origin is dict :
            if len(args) != 2 :
                raise ValueError("Malformed dict annotation: expected dict[K, V]")

            key_type = self.resolve(args[ 0 ])
            value_type = self.resolve(args[ 1 ])
            return DictTypeSpec(
                key_type = key_type,
                value_type = value_type,
            )

        raise ValueError(f"Unsupported annotation: {annotation!r}")
