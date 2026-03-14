import pytest

from alg_o.generation import SignatureGenerator

from .helpers import SIZE_CASES, SUPPORTED_TYPE_CASES


@pytest.mark.parametrize("case", SUPPORTED_TYPE_CASES, ids = lambda case : case.case_id)
def test_signature_generator_resolves_expected_type_name( case ) -> None :
    signature_generator = SignatureGenerator.from_function(case.function)
    parameter = signature_generator.parameters[ 0 ]

    assert len(signature_generator.parameters) == 1
    assert parameter.type_spec.name == case.expected_name


@pytest.mark.parametrize("case", SUPPORTED_TYPE_CASES, ids = lambda case : case.case_id)
def test_signature_generator_preserves_parameter_name( case ) -> None :
    signature_generator = SignatureGenerator.from_function(case.function)
    parameter = signature_generator.parameters[ 0 ]

    assert parameter.name == case.parameter_name


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
@pytest.mark.parametrize("case", SUPPORTED_TYPE_CASES, ids = lambda case : case.case_id)
def test_generate_arguments_returns_expected_parameter_key( case, size: int ) -> None :
    signature_generator = SignatureGenerator.from_function(case.function)
    arguments = signature_generator.generate_arguments(size)

    assert set(arguments.keys()) == { case.parameter_name }


@pytest.mark.parametrize("size", SIZE_CASES, ids = lambda size : f"size-{size}")
@pytest.mark.parametrize("case", SUPPORTED_TYPE_CASES, ids = lambda case : case.case_id)
def test_generate_arguments_returns_expected_top_level_type( case, size: int ) -> None :
    signature_generator = SignatureGenerator.from_function(case.function)
    arguments = signature_generator.generate_arguments(size)

    assert isinstance(arguments[ case.parameter_name ], case.top_level_type)
