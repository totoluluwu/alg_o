from statistics import mean

import pytest

from alg_o.benchmark import BenchmarkRunner

from .helpers import BENCHMARK_SCENARIOS


@pytest.fixture(
    scope = "module",
    params = BENCHMARK_SCENARIOS,
    ids = lambda scenario : scenario.case_id,
)
def benchmark_run( request ) :
    scenario = request.param
    config = scenario.config_factory()
    runner = BenchmarkRunner(config)
    result = runner.run(scenario.function)
    return scenario, config, result


def test_benchmark_runner_sets_expected_function_name( benchmark_run ) -> None :
    scenario, _, result = benchmark_run

    assert result.function_name == scenario.function.__name__


def test_benchmark_runner_preserves_configured_sizes( benchmark_run ) -> None :
    _, config, result = benchmark_run

    assert result.sizes == config.sizes


def test_benchmark_runner_returns_one_point_per_size( benchmark_run ) -> None :
    _, config, result = benchmark_run

    assert len(result.points) == len(config.sizes)


def test_benchmark_runner_point_sizes_follow_config_order( benchmark_run ) -> None :
    _, config, result = benchmark_run

    assert [ point.size for point in result.points ] == config.sizes


def test_benchmark_runner_respects_repeat_count_for_each_point( benchmark_run ) -> None :
    _, config, result = benchmark_run

    assert all(len(point.times) == config.repeat for point in result.points)


def test_benchmark_runner_measurements_are_non_negative( benchmark_run ) -> None :
    _, _, result = benchmark_run

    assert all(
        measured_time >= 0.0
        for point in result.points
        for measured_time in point.times
    )


def test_benchmark_runner_average_time_is_non_negative( benchmark_run ) -> None :
    _, _, result = benchmark_run

    assert all(point.average_time >= 0.0 for point in result.points)


def test_benchmark_runner_average_matches_measured_mean( benchmark_run ) -> None :
    _, _, result = benchmark_run

    assert all(
        point.average_time == pytest.approx(mean(point.times), abs = 1e-12)
        for point in result.points
    )
