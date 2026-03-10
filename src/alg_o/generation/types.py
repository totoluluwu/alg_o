from dataclasses import dataclass

from .base import TypeSpec


@dataclass(frozen = True)
class IntTypeSpec(TypeSpec) :
    """Type specification for int"""

    @property
    def name( self ) -> str :
        return "int"


@dataclass(frozen = True)
class FloatTypeSpec(TypeSpec) :
    """Type specification for float"""

    @property
    def name( self ) -> str :
        return "float"


@dataclass(frozen = True)
class StringTypeSpec(TypeSpec) :
    """Type specification for str"""

    @property
    def name( self ) -> str :
        return "str"


@dataclass(frozen = True)
class ListTypeSpec(TypeSpec) :
    """Type specification for list[T]"""

    element_type: TypeSpec

    @property
    def name( self ) -> str :
        return f"list[{self.element_type.name}]"


@dataclass(frozen = True)
class DictTypeSpec(TypeSpec) :
    """Type specification for dict[K, V]"""

    key_type: TypeSpec
    value_type: TypeSpec

    @property
    def name( self ) -> str :
        return f"dict[{self.key_type.name}, {self.value_type.name}]"
