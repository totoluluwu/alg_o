import pytest

from alg_o.analysis import AnalysisResult, ComplexityEstimator
from alg_o.benchmark import BenchmarkRunner

from .helpers import ANALYSIS_SCENARIOS


@pytest.fixture(
    scope = "module",
    params = ANALYSIS_SCENARIOS,
    ids = lambda scenario : scenario.case_id,
)
def analysis_run( request ) :
    scenario = request.param
    config = scenario.config_factory()
    estimator = ComplexityEstimator(
        benchmark_runner = BenchmarkRunner(config),
    )
    result = estimator.estimate(scenario.function)
    return scenario, config, result


def test_estimator_returns_analysis_result_instance( analysis_run ) -> None :
    _, _, result = analysis_run

    assert isinstance(result, AnalysisResult)


def test_estimator_preserves_function_name( analysis_run ) -> None :
    scenario, _, result = analysis_run

    assert result.function_name == scenario.function.__name__


def test_estimator_preserves_configured_sizes( analysis_run ) -> None :
    _, config, result = analysis_run

    assert result.sizes == config.sizes


def test_estimator_returns_time_per_size( analysis_run ) -> None :
    _, config, result = analysis_run

    assert len(result.times) == len(config.sizes)


def test_estimator_returns_non_negative_times( analysis_run ) -> None :
    _, _, result = analysis_run

    assert all(measured_time >= 0.0 for measured_time in result.times)


def test_estimator_best_complexity_is_supported_model_name( analysis_run ) -> None :
    _, _, result = analysis_run

    assert result.best_complexity in {
        "O(1)",
        "O(log n)",
        "O(n)",
        "O(n log n)",
        "O(n^2)",
        "O(n^3)",
    }


def test_estimator_best_complexity_is_in_expected_set( analysis_run ) -> None :
    scenario, _, result = analysis_run

    assert result.best_complexity in scenario.accepted_models


def test_estimator_regression_sizes_match_benchmark_sizes( analysis_run ) -> None :
    _, _, result = analysis_run

    assert result.regression_result.sizes == result.benchmark_result.sizes


def test_estimator_regression_times_match_benchmark_averages( analysis_run ) -> None :
    _, _, result = analysis_run

    assert result.regression_result.observed_times == result.benchmark_result.average_times
