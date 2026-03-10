import pathlib
import random
import sys
import typing
import unittest
from dataclasses import FrozenInstanceError


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))

from alg_o import generation
from alg_o.generation import (
    DataGenerator,
    DictGenerator,
    DictTypeSpec,
    FloatGenerator,
    FloatTypeSpec,
    IntGenerator,
    IntTypeSpec,
    ListGenerator,
    ListTypeSpec,
    ParameterSpec,
    SignatureGenerator,
    StringGenerator,
    StringTypeSpec,
    TypeResolver,
    TypeSpec,
    build_generator,
)


class UnsupportedSpec(TypeSpec) :

    @property
    def name( self ) -> str :
        return "unsupported"


class ConstantGenerator(DataGenerator) :

    def __init__( self, value: object ) -> None :
        self._value = value

    def generate( self, size: int ) -> object :
        _ = size
        return self._value


class SequenceIntGenerator(DataGenerator) :

    def __init__( self ) -> None :
        self._value = 0
        self.received_sizes: list[ int ] = [ ]

    def generate( self, size: int ) -> object :
        self.received_sizes.append(size)
        current = self._value
        self._value += 1
        return current


class EchoSizeGenerator(DataGenerator) :

    def __init__( self ) -> None :
        self.received_sizes: list[ int ] = [ ]

    def generate( self, size: int ) -> object :
        self.received_sizes.append(size)
        return size


class GenerationBaseTests(unittest.TestCase) :

    def test_type_spec_is_abstract( self ) -> None :
        with self.assertRaises(TypeError) :
            TypeSpec()

    def test_data_generator_is_abstract( self ) -> None :
        with self.assertRaises(TypeError) :
            DataGenerator()


class GenerationTypesTests(unittest.TestCase) :

    def test_primitive_type_specs_names( self ) -> None :
        self.assertEqual(IntTypeSpec().name, "int")
        self.assertEqual(FloatTypeSpec().name, "float")
        self.assertEqual(StringTypeSpec().name, "str")

    def test_nested_type_specs_names( self ) -> None :
        list_spec = ListTypeSpec(element_type = IntTypeSpec())
        dict_spec = DictTypeSpec(
            key_type = StringTypeSpec(),
            value_type = list_spec,
        )
        self.assertEqual(list_spec.name, "list[int]")
        self.assertEqual(dict_spec.name, "dict[str, list[int]]")

    def test_type_specs_are_frozen( self ) -> None :
        with self.assertRaises(FrozenInstanceError) :
            ListTypeSpec(element_type = IntTypeSpec()).element_type = FloatTypeSpec()


class GenerationGeneratorsTests(unittest.TestCase) :

    def setUp( self ) -> None :
        random.seed(42)

    def test_int_generator_range( self ) -> None :
        value = IntGenerator().generate(5)
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, -5)
        self.assertLessEqual(value, 5)

    def test_float_generator_range( self ) -> None :
        value = FloatGenerator().generate(7)
        self.assertIsInstance(value, float)
        self.assertGreaterEqual(value, -7.0)
        self.assertLessEqual(value, 7.0)

    def test_string_generator_length( self ) -> None :
        value = StringGenerator().generate(9)
        self.assertIsInstance(value, str)
        self.assertEqual(len(value), 9)

    def test_generators_validate_positive_size( self ) -> None :
        with self.assertRaisesRegex(ValueError, "strictly positive") :
            IntGenerator().generate(0)
        with self.assertRaisesRegex(ValueError, "strictly positive") :
            FloatGenerator().generate(-1)
        with self.assertRaisesRegex(ValueError, "strictly positive") :
            StringGenerator().generate(0)

    def test_list_generator_uses_reduced_child_size( self ) -> None :
        child = EchoSizeGenerator()
        generator = ListGenerator(element_generator = child)
        values = generator.generate(6)

        self.assertEqual(len(values), 6)
        self.assertEqual(values, [ 3, 3, 3, 3, 3, 3 ])
        self.assertEqual(child.received_sizes, [ 3, 3, 3, 3, 3, 3 ])

    def test_list_generator_uses_child_size_one( self ) -> None :
        child = EchoSizeGenerator()
        generator = ListGenerator(element_generator = child)
        values = generator.generate(1)

        self.assertEqual(values, [ 1 ])
        self.assertEqual(child.received_sizes, [ 1 ])

    def test_dict_generator_with_unique_keys( self ) -> None :
        key_generator = SequenceIntGenerator()
        value_generator = EchoSizeGenerator()
        generator = DictGenerator(
            key_generator = key_generator,
            value_generator = value_generator,
        )
        values = generator.generate(4)

        self.assertEqual(len(values), 4)
        self.assertEqual(set(values.keys()), { 0, 1, 2, 3 })
        self.assertEqual(list(values.values()), [ 2, 2, 2, 2 ])
        self.assertEqual(key_generator.received_sizes, [ 2, 2, 2, 2 ])
        self.assertEqual(value_generator.received_sizes, [ 2, 2, 2, 2 ])

    def test_dict_generator_duplicate_keys_raises( self ) -> None :
        generator = DictGenerator(
            key_generator = ConstantGenerator("same-key"),
            value_generator = ConstantGenerator(1),
        )

        with self.assertRaisesRegex(ValueError, "Unable to generate enough unique") :
            generator.generate(3)

    def test_dict_generator_validate_positive_size( self ) -> None :
        generator = DictGenerator(
            key_generator = ConstantGenerator("a"),
            value_generator = ConstantGenerator(1),
        )
        with self.assertRaisesRegex(ValueError, "strictly positive") :
            generator.generate(0)

    def test_build_generator_primitives( self ) -> None :
        self.assertIsInstance(build_generator(IntTypeSpec()), IntGenerator)
        self.assertIsInstance(build_generator(FloatTypeSpec()), FloatGenerator)
        self.assertIsInstance(build_generator(StringTypeSpec()), StringGenerator)

    def test_build_generator_nested( self ) -> None :
        list_spec = ListTypeSpec(element_type = IntTypeSpec())
        dict_spec = DictTypeSpec(
            key_type = StringTypeSpec(),
            value_type = list_spec,
        )

        list_generator = build_generator(list_spec)
        dict_generator = build_generator(dict_spec)

        self.assertIsInstance(list_generator, ListGenerator)
        self.assertIsInstance(dict_generator, DictGenerator)

    def test_build_generator_rejects_unsupported_dict_key_type( self ) -> None :
        dict_spec = DictTypeSpec(
            key_type = ListTypeSpec(element_type = IntTypeSpec()),
            value_type = IntTypeSpec(),
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dictionary key type") :
            build_generator(dict_spec)

    def test_build_generator_rejects_unsupported_spec( self ) -> None :
        with self.assertRaisesRegex(ValueError, "Unsupported type specification") :
            build_generator(UnsupportedSpec())


class GenerationResolverTests(unittest.TestCase) :

    def setUp( self ) -> None :
        self.resolver = TypeResolver()

    def test_resolve_primitive_types( self ) -> None :
        self.assertIsInstance(self.resolver.resolve(int), IntTypeSpec)
        self.assertIsInstance(self.resolver.resolve(float), FloatTypeSpec)
        self.assertIsInstance(self.resolver.resolve(str), StringTypeSpec)

    def test_resolve_list_type( self ) -> None :
        spec = self.resolver.resolve(list[ int ])
        self.assertIsInstance(spec, ListTypeSpec)
        assert isinstance(spec, ListTypeSpec)
        self.assertIsInstance(spec.element_type, IntTypeSpec)

    def test_resolve_dict_type( self ) -> None :
        spec = self.resolver.resolve(dict[ str, float ])
        self.assertIsInstance(spec, DictTypeSpec)
        assert isinstance(spec, DictTypeSpec)
        self.assertIsInstance(spec.key_type, StringTypeSpec)
        self.assertIsInstance(spec.value_type, FloatTypeSpec)

    def test_resolve_nested_types( self ) -> None :
        spec = self.resolver.resolve(dict[ str, list[ int ] ])
        self.assertIsInstance(spec, DictTypeSpec)
        assert isinstance(spec, DictTypeSpec)
        self.assertIsInstance(spec.value_type, ListTypeSpec)

    def test_resolve_malformed_list_builtin( self ) -> None :
        with self.assertRaisesRegex(ValueError, "Malformed list annotation") :
            self.resolver.resolve(list)

    def test_resolve_malformed_dict_builtin( self ) -> None :
        with self.assertRaisesRegex(ValueError, "Malformed dict annotation") :
            self.resolver.resolve(dict)

    def test_resolve_malformed_list_typing( self ) -> None :
        with self.assertRaisesRegex(ValueError, "Malformed list annotation") :
            self.resolver.resolve(typing.List)

    def test_resolve_malformed_dict_typing( self ) -> None :
        with self.assertRaisesRegex(ValueError, "Malformed dict annotation") :
            self.resolver.resolve(typing.Dict)

    def test_resolve_unsupported_type( self ) -> None :
        with self.assertRaisesRegex(ValueError, "Unsupported annotation") :
            self.resolver.resolve(bool)


class GenerationSignatureTests(unittest.TestCase) :

    def setUp( self ) -> None :
        random.seed(123)

    def test_from_function_builds_parameters_and_generators( self ) -> None :
        def target( a: int, b: list[ str ], c: dict[ str, list[ int ] ] ) -> None :
            _ = (a, b, c)

        signature_generator = SignatureGenerator.from_function(target)
        parameter_names = [ parameter.name for parameter in signature_generator.parameters ]

        self.assertEqual(parameter_names, [ "a", "b", "c" ])
        self.assertEqual(signature_generator.parameters[ 0 ].type_spec.name, "int")
        self.assertEqual(signature_generator.parameters[ 1 ].type_spec.name, "list[str]")
        self.assertEqual(
            signature_generator.parameters[ 2 ].type_spec.name,
            "dict[str, list[int]]",
        )

    def test_from_function_without_annotation_raises( self ) -> None :
        def target( a, b: int ) -> None :
            _ = (a, b)

        with self.assertRaisesRegex(ValueError, "has no type annotation") :
            SignatureGenerator.from_function(target)

    def test_from_function_with_unsupported_annotation_raises( self ) -> None :
        def target( a: bool ) -> None :
            _ = a

        with self.assertRaisesRegex(ValueError, "Unsupported annotation") :
            SignatureGenerator.from_function(target)

    def test_from_function_with_unsupported_dict_key_raises( self ) -> None :
        def target( a: dict[ list[ int ], int ] ) -> None :
            _ = a

        with self.assertRaisesRegex(ValueError, "Unsupported dictionary key type") :
            SignatureGenerator.from_function(target)

    def test_generate_arguments( self ) -> None :
        def target(
                a: int,
                b: list[ str ],
                c: dict[ str, list[ int ] ],
        ) -> None :
            _ = (a, b, c)

        signature_generator = SignatureGenerator.from_function(target)
        values = signature_generator.generate_arguments(6)

        self.assertEqual(set(values.keys()), { "a", "b", "c" })
        self.assertIsInstance(values[ "a" ], int)
        self.assertIsInstance(values[ "b" ], list)
        self.assertEqual(len(values[ "b" ]), 6)
        self.assertTrue(all(isinstance(item, str) for item in values[ "b" ]))
        self.assertTrue(all(len(item) == 3 for item in values[ "b" ]))

        self.assertIsInstance(values[ "c" ], dict)
        self.assertEqual(len(values[ "c" ]), 6)
        self.assertTrue(all(isinstance(key, str) for key in values[ "c" ].keys()))
        self.assertTrue(all(isinstance(item, list) for item in values[ "c" ].values()))
        self.assertTrue(all(len(item) == 3 for item in values[ "c" ].values()))
        for item in values[ "c" ].values() :
            self.assertTrue(all(isinstance(number, int) for number in item))

    def test_generate_arguments_with_invalid_size( self ) -> None :
        def target( a: int ) -> None :
            _ = a

        signature_generator = SignatureGenerator.from_function(target)
        with self.assertRaisesRegex(ValueError, "strictly positive") :
            signature_generator.generate_arguments(0)

    def test_generate_arguments_no_parameter_function( self ) -> None :
        def target() -> None :
            return None

        signature_generator = SignatureGenerator.from_function(target)
        self.assertEqual(signature_generator.generate_arguments(4), { })

    def test_parameters_property_returns_copy( self ) -> None :
        def target( a: int, b: str ) -> None :
            _ = (a, b)

        signature_generator = SignatureGenerator.from_function(target)
        parameters = signature_generator.parameters
        parameters.append(ParameterSpec(name = "x", type_spec = IntTypeSpec()))

        self.assertEqual(
            [ parameter.name for parameter in signature_generator.parameters ],
            [ "a", "b" ],
        )


class GenerationPublicApiTests(unittest.TestCase) :

    def test_package_exports( self ) -> None :
        expected = {
            "TypeSpec",
            "DataGenerator",
            "IntTypeSpec",
            "FloatTypeSpec",
            "StringTypeSpec",
            "ListTypeSpec",
            "DictTypeSpec",
            "IntGenerator",
            "FloatGenerator",
            "StringGenerator",
            "ListGenerator",
            "DictGenerator",
            "build_generator",
            "TypeResolver",
            "ParameterSpec",
            "SignatureGenerator",
        }
        self.assertEqual(set(generation.__all__), expected)

    def test_public_imports_work( self ) -> None :
        self.assertTrue(issubclass(IntTypeSpec, TypeSpec))
        self.assertTrue(issubclass(IntGenerator, DataGenerator))
        self.assertIsInstance(TypeResolver(), TypeResolver)


if __name__ == "__main__" :
    unittest.main()
