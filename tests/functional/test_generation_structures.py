import pytest

from alg_o.generation import SignatureGenerator

from .helpers import SIZE_CASES
from .helpers import (
    typed_dict_str_int,
    typed_dict_str_list_int,
    typed_list_dict_str_float,
    typed_list_int,
    typed_list_str,
    typed_str,
)


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_string_matches_requested_size( size: int ) -> None :
    signature_generator = SignatureGenerator.from_function(typed_str)
    arguments = signature_generator.generate_arguments(size)
    value = arguments[ "value" ]

    assert isinstance(value, str)
    assert len(value) == size


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_list_int_has_expected_shape( size: int ) -> None :
    signature_generator = SignatureGenerator.from_function(typed_list_int)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert isinstance(values, list)
    assert len(values) == size
    assert all(isinstance(item, int) for item in values)


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_list_str_has_expected_shape( size: int ) -> None :
    signature_generator = SignatureGenerator.from_function(typed_list_str)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert isinstance(values, list)
    assert len(values) == size
    assert all(isinstance(item, str) for item in values)


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_list_str_uses_expected_child_string_size( size: int ) -> None :
    expected_child_size = max(1, size // 2)
    signature_generator = SignatureGenerator.from_function(typed_list_str)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert all(len(item) == expected_child_size for item in values)


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_dict_str_int_has_expected_shape( size: int ) -> None :
    signature_generator = SignatureGenerator.from_function(typed_dict_str_int)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert isinstance(values, dict)
    assert len(values) == size
    assert all(isinstance(key, str) for key in values.keys())
    assert all(isinstance(item, int) for item in values.values())


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_dict_str_int_keys_use_expected_child_string_size( size: int ) -> None :
    expected_child_size = max(1, size // 2)
    signature_generator = SignatureGenerator.from_function(typed_dict_str_int)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert all(len(key) == expected_child_size for key in values.keys())


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_dict_str_list_int_has_expected_nested_shape( size: int ) -> None :
    expected_child_size = max(1, size // 2)
    signature_generator = SignatureGenerator.from_function(typed_dict_str_list_int)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert isinstance(values, dict)
    assert len(values) == size
    assert all(isinstance(key, str) for key in values.keys())
    assert all(len(key) == expected_child_size for key in values.keys())
    assert all(isinstance(item, list) for item in values.values())
    assert all(len(item) == expected_child_size for item in values.values())
    assert all(
        isinstance(number, int)
        for item in values.values()
        for number in item
    )


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
def test_generated_list_dict_str_float_has_expected_nested_shape( size: int ) -> None :
    outer_child_size = max(1, size // 2)
    inner_child_size = max(1, outer_child_size // 2)
    signature_generator = SignatureGenerator.from_function(typed_list_dict_str_float)
    arguments = signature_generator.generate_arguments(size)
    values = arguments[ "values" ]

    assert isinstance(values, list)
    assert len(values) == size
    assert all(isinstance(item, dict) for item in values)
    assert all(len(item) == outer_child_size for item in values)
    assert all(
        len(key) == inner_child_size
        for item in values
        for key in item.keys()
    )
    assert all(
        isinstance(number, float)
        for item in values
        for number in item.values()
    )
