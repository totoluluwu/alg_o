import pytest

from alg_o.regression import RegressionEngine

from .helpers import REGRESSION_SYNTHETIC_CASES


@pytest.fixture(
    scope = "module",
    params = REGRESSION_SYNTHETIC_CASES,
    ids = lambda case : case.case_id,
)
def fitted_regression_case( request ) :
    case = request.param
    result = RegressionEngine().fit(
        list(case.sizes),
        list(case.times),
    )
    return case, result


def test_regression_selects_expected_best_model( fitted_regression_case ) -> None :
    case, result = fitted_regression_case

    assert result.best_fit.model_name == case.expected_model


def test_regression_returns_matching_fit_for_expected_model( fitted_regression_case ) -> None :
    case, result = fitted_regression_case
    fit = result.get_fit(case.expected_model)

    assert fit is not None


def test_regression_matching_fit_has_expected_prediction_count( fitted_regression_case ) -> None :
    case, result = fitted_regression_case
    fit = result.get_fit(case.expected_model)
    assert fit is not None

    assert len(fit.predicted_times) == len(case.sizes)


def test_regression_best_fit_coefficient_is_positive( fitted_regression_case ) -> None :
    _, result = fitted_regression_case

    assert result.best_fit.coefficient > 0.0


def test_regression_matching_fit_coefficient_is_positive( fitted_regression_case ) -> None :
    case, result = fitted_regression_case
    fit = result.get_fit(case.expected_model)
    assert fit is not None

    assert fit.coefficient > 0.0


def test_regression_matching_fit_error_is_near_zero( fitted_regression_case ) -> None :
    case, result = fitted_regression_case
    fit = result.get_fit(case.expected_model)
    assert fit is not None

    assert fit.error == pytest.approx(0.0, abs = 1e-12)


def test_regression_best_fit_error_is_near_zero( fitted_regression_case ) -> None :
    _, result = fitted_regression_case

    assert result.best_fit.error == pytest.approx(0.0, abs = 1e-12)


def test_regression_best_fit_is_in_model_fit_list( fitted_regression_case ) -> None :
    _, result = fitted_regression_case

    assert result.best_fit in result.model_fits


def test_regression_keeps_original_sizes( fitted_regression_case ) -> None :
    case, result = fitted_regression_case

    assert result.sizes == list(case.sizes)


def test_regression_keeps_original_observed_times( fitted_regression_case ) -> None :
    case, result = fitted_regression_case

    assert result.observed_times == list(case.times)
