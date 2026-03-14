from dataclasses import dataclass
from math import log2
from typing import Callable

from alg_o.benchmark import BenchmarkConfig


SIZE_CASES = [ 1, 4, 8 ]
REGRESSION_SIZES = (8, 16, 32, 64, 128, 256)


def typed_int( value: int ) -> int :
    return value + 1


def typed_float( value: float ) -> float :
    return value + 1.0


def typed_str( value: str ) -> int :
    return len(value)


def typed_list_int( values: list[ int ] ) -> int :
    return sum(values)


def typed_list_str( values: list[ str ] ) -> int :
    return sum(len(item) for item in values)


def typed_dict_str_int( values: dict[ str, int ] ) -> int :
    return sum(values.values())


def typed_dict_str_list_int( values: dict[ str, list[ int ] ] ) -> int :
    return sum(sum(item) for item in values.values())


def typed_list_dict_str_float( values: list[ dict[ str, float ] ] ) -> int :
    return sum(len(item) for item in values)


def benchmark_int( value: int ) -> int :
    accumulator = 0
    for _ in range(50) :
        accumulator += value & 7
    return accumulator


def benchmark_str( value: str ) -> int :
    accumulator = 0
    for character in value :
        accumulator += ord(character) & 15
    return accumulator


def benchmark_list_int( values: list[ int ] ) -> int :
    accumulator = 0
    for number in values :
        accumulator += number & 7
    return accumulator


def benchmark_dict_str_int( values: dict[ str, int ] ) -> int :
    accumulator = 0
    for number in values.values() :
        accumulator += number & 7
    return accumulator


def benchmark_dict_str_list_int( values: dict[ str, list[ int ] ] ) -> int :
    accumulator = 0
    for numbers in values.values() :
        for number in numbers :
            accumulator += number & 3
    return accumulator


def analysis_constant_float( value: float ) -> int :
    _ = value
    accumulator = 0
    for index in range(6000) :
        accumulator += (index * 7) % 11
    return accumulator


def analysis_logarithmic_str( value: str ) -> int :
    accumulator = 0
    for _ in range(220) :
        low = 0
        high = len(value) - 1
        while low <= high :
            middle = (low + high) // 2
            accumulator += middle & 1
            if middle % 2 == 0 :
                low = middle + 1
            else :
                high = middle - 1
    return accumulator


def analysis_linear_dict( values: dict[ str, int ] ) -> int :
    accumulator = 0
    numbers = list(values.values())
    for _ in range(40) :
        for number in numbers :
            accumulator += number & 3
    return accumulator


def analysis_linearithmic_list( values: list[ int ] ) -> int :
    accumulator = 0
    for _ in range(30) :
        ordered = sorted(values)
        if ordered :
            accumulator += ordered[ len(ordered) // 2 ]
    return accumulator


def analysis_quadratic_nested( values: list[ dict[ str, float ] ] ) -> int :
    accumulator = 0
    lengths = [ len(item) for item in values ]
    for left in lengths :
        for right in lengths :
            accumulator += (left + right) & 1
    return accumulator


def make_light_benchmark_config() -> BenchmarkConfig :
    return BenchmarkConfig(
        sizes = [ 4, 8 ],
        repeat = 1,
        warmup = 0,
    )


def make_moderate_benchmark_config() -> BenchmarkConfig :
    return BenchmarkConfig(
        sizes = [ 10, 20, 40 ],
        repeat = 2,
        warmup = 1,
    )


def make_standard_analysis_config() -> BenchmarkConfig :
    return BenchmarkConfig(
        sizes = [ 50, 100, 200, 400, 800 ],
        repeat = 3,
        warmup = 1,
    )


def make_compact_analysis_config() -> BenchmarkConfig :
    return BenchmarkConfig(
        sizes = [ 40, 80, 160, 320 ],
        repeat = 2,
        warmup = 1,
    )


def make_heavy_analysis_config() -> BenchmarkConfig :
    return BenchmarkConfig(
        sizes = [ 10, 20, 40, 80, 120 ],
        repeat = 3,
        warmup = 1,
    )


@dataclass(frozen = True)
class SupportedTypeCase :
    case_id: str
    function: Callable[ ..., object ]
    expected_name: str
    parameter_name: str
    top_level_type: type


@dataclass(frozen = True)
class RegressionSyntheticCase :
    case_id: str
    expected_model: str
    sizes: tuple[ int, ... ]
    times: tuple[ float, ... ]


@dataclass(frozen = True)
class BenchmarkScenario :
    case_id: str
    function: Callable[ ..., object ]
    config_factory: Callable[ ..., BenchmarkConfig ]


@dataclass(frozen = True)
class AnalysisScenario :
    case_id: str
    function: Callable[ ..., object ]
    config_factory: Callable[ ..., BenchmarkConfig ]
    accepted_models: frozenset[ str ]


SUPPORTED_TYPE_CASES = [
    SupportedTypeCase(
        case_id = "int",
        function = typed_int,
        expected_name = "int",
        parameter_name = "value",
        top_level_type = int,
    ),
    SupportedTypeCase(
        case_id = "float",
        function = typed_float,
        expected_name = "float",
        parameter_name = "value",
        top_level_type = float,
    ),
    SupportedTypeCase(
        case_id = "str",
        function = typed_str,
        expected_name = "str",
        parameter_name = "value",
        top_level_type = str,
    ),
    SupportedTypeCase(
        case_id = "list-int",
        function = typed_list_int,
        expected_name = "list[int]",
        parameter_name = "values",
        top_level_type = list,
    ),
    SupportedTypeCase(
        case_id = "list-str",
        function = typed_list_str,
        expected_name = "list[str]",
        parameter_name = "values",
        top_level_type = list,
    ),
    SupportedTypeCase(
        case_id = "dict-str-int",
        function = typed_dict_str_int,
        expected_name = "dict[str, int]",
        parameter_name = "values",
        top_level_type = dict,
    ),
    SupportedTypeCase(
        case_id = "dict-str-list-int",
        function = typed_dict_str_list_int,
        expected_name = "dict[str, list[int]]",
        parameter_name = "values",
        top_level_type = dict,
    ),
    SupportedTypeCase(
        case_id = "list-dict-str-float",
        function = typed_list_dict_str_float,
        expected_name = "list[dict[str, float]]",
        parameter_name = "values",
        top_level_type = list,
    ),
]

SUPPORTED_TYPE_CASE_BY_ID = {
    case.case_id : case
    for case in SUPPORTED_TYPE_CASES
}


def _times_constant( scale: float ) -> tuple[ float, ... ] :
    return tuple(scale for _ in REGRESSION_SIZES)


def _times_logarithmic( scale: float ) -> tuple[ float, ... ] :
    return tuple(scale * log2(size) for size in REGRESSION_SIZES)


def _times_linear( scale: float ) -> tuple[ float, ... ] :
    return tuple(scale * size for size in REGRESSION_SIZES)


def _times_linearithmic( scale: float ) -> tuple[ float, ... ] :
    return tuple(scale * size * log2(size) for size in REGRESSION_SIZES)


def _times_quadratic( scale: float ) -> tuple[ float, ... ] :
    return tuple(scale * size * size for size in REGRESSION_SIZES)


REGRESSION_SYNTHETIC_CASES = [
    RegressionSyntheticCase(
        case_id = "constant-base",
        expected_model = "O(1)",
        sizes = REGRESSION_SIZES,
        times = _times_constant(2.0),
    ),
    RegressionSyntheticCase(
        case_id = "constant-scaled",
        expected_model = "O(1)",
        sizes = REGRESSION_SIZES,
        times = _times_constant(9.5),
    ),
    RegressionSyntheticCase(
        case_id = "logarithmic-base",
        expected_model = "O(log n)",
        sizes = REGRESSION_SIZES,
        times = _times_logarithmic(0.4),
    ),
    RegressionSyntheticCase(
        case_id = "logarithmic-scaled",
        expected_model = "O(log n)",
        sizes = REGRESSION_SIZES,
        times = _times_logarithmic(1.7),
    ),
    RegressionSyntheticCase(
        case_id = "linear-base",
        expected_model = "O(n)",
        sizes = REGRESSION_SIZES,
        times = _times_linear(0.03),
    ),
    RegressionSyntheticCase(
        case_id = "linear-scaled",
        expected_model = "O(n)",
        sizes = REGRESSION_SIZES,
        times = _times_linear(0.12),
    ),
    RegressionSyntheticCase(
        case_id = "linearithmic-base",
        expected_model = "O(n log n)",
        sizes = REGRESSION_SIZES,
        times = _times_linearithmic(0.004),
    ),
    RegressionSyntheticCase(
        case_id = "linearithmic-scaled",
        expected_model = "O(n log n)",
        sizes = REGRESSION_SIZES,
        times = _times_linearithmic(0.02),
    ),
    RegressionSyntheticCase(
        case_id = "quadratic-base",
        expected_model = "O(n^2)",
        sizes = REGRESSION_SIZES,
        times = _times_quadratic(0.0004),
    ),
    RegressionSyntheticCase(
        case_id = "quadratic-scaled",
        expected_model = "O(n^2)",
        sizes = REGRESSION_SIZES,
        times = _times_quadratic(0.001),
    ),
]

_BENCHMARK_FUNCTIONS = [
    benchmark_int,
    benchmark_str,
    benchmark_list_int,
    benchmark_dict_str_int,
    benchmark_dict_str_list_int,
]

BENCHMARK_SCENARIOS = [
    BenchmarkScenario(
        case_id = f"{function.__name__}-light",
        function = function,
        config_factory = make_light_benchmark_config,
    )
    for function in _BENCHMARK_FUNCTIONS
]
BENCHMARK_SCENARIOS += [
    BenchmarkScenario(
        case_id = f"{function.__name__}-moderate",
        function = function,
        config_factory = make_moderate_benchmark_config,
    )
    for function in _BENCHMARK_FUNCTIONS
]

ANALYSIS_SCENARIOS = [
    AnalysisScenario(
        case_id = "constant-standard",
        function = analysis_constant_float,
        config_factory = make_standard_analysis_config,
        accepted_models = frozenset({ "O(1)", "O(log n)" }),
    ),
    AnalysisScenario(
        case_id = "constant-compact",
        function = analysis_constant_float,
        config_factory = make_compact_analysis_config,
        accepted_models = frozenset({ "O(1)", "O(log n)" }),
    ),
    AnalysisScenario(
        case_id = "logarithmic-standard",
        function = analysis_logarithmic_str,
        config_factory = make_standard_analysis_config,
        accepted_models = frozenset({ "O(log n)", "O(n)" }),
    ),
    AnalysisScenario(
        case_id = "logarithmic-compact",
        function = analysis_logarithmic_str,
        config_factory = make_compact_analysis_config,
        accepted_models = frozenset({ "O(log n)", "O(n)" }),
    ),
    AnalysisScenario(
        case_id = "linear-standard",
        function = analysis_linear_dict,
        config_factory = make_standard_analysis_config,
        accepted_models = frozenset({ "O(n)", "O(n log n)" }),
    ),
    AnalysisScenario(
        case_id = "linear-compact",
        function = analysis_linear_dict,
        config_factory = make_compact_analysis_config,
        accepted_models = frozenset({ "O(n)", "O(n log n)" }),
    ),
    AnalysisScenario(
        case_id = "linearithmic-heavy",
        function = analysis_linearithmic_list,
        config_factory = make_heavy_analysis_config,
        accepted_models = frozenset({ "O(n log n)", "O(n^2)" }),
    ),
    AnalysisScenario(
        case_id = "quadratic-heavy",
        function = analysis_quadratic_nested,
        config_factory = make_heavy_analysis_config,
        accepted_models = frozenset({ "O(n^2)", "O(n^3)" }),
    ),
]
