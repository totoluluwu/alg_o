from ..exception import RegressionError
from .base import ComplexityModel
from .models import (
    ConstantModel,
    CubicModel,
    LinearModel,
    LinearithmicModel,
    LogarithmicModel,
    QuadraticModel,
)
from .result import ModelFitResult, RegressionResult


class RegressionEngine :
    """Fit measured runtimes against complexity models"""

    def __init__( self, models: list[ ComplexityModel ] | None = None ) -> None :
        """Create the engine with default models or user-provided ones"""
        if models is None :
            models = [
                ConstantModel(),
                LogarithmicModel(),
                LinearModel(),
                LinearithmicModel(),
                QuadraticModel(),
                CubicModel(),
            ]
        self._models = list(models)
        if len(self._models) == 0 :
            raise RegressionError("At least one complexity model must be provided.")

    def fit( self, sizes: list[ int ], times: list[ float ] ) -> RegressionResult :
        """Fit all models and return every fit plus the best one"""
        self._validate_inputs(sizes, times)

        fit_results: list[ ModelFitResult ] = [ ]
        for model in self._models :
            fit_results.append(self._fit_one_model(model, sizes, times))

        best_fit = min(fit_results, key = lambda fit : fit.error)

        return RegressionResult(
            sizes = list(sizes),
            observed_times = list(times),
            model_fits = fit_results,
            best_fit = best_fit,
        )

    @staticmethod
    def _validate_inputs( sizes: list[ int ], times: list[ float ] ) -> None :
        """Validate input data"""
        if len(sizes) != len(times) :
            raise RegressionError("sizes and times must have the same length.")
        if not sizes :
            raise RegressionError("sizes and times must not be empty.")
        for size in sizes :
            if size <= 0 :
                raise RegressionError("All sizes must be strictly positive.")
        for time in times :
            if time < 0 :
                raise RegressionError("All times must be non-negative.")

    def _fit_one_model(
            self, model: ComplexityModel, sizes: list[ int ], times: list[ float ],
    ) -> ModelFitResult :
        """Fit one model with y ~= a*x and compute MSE"""
        x_values = model.evaluate_all(sizes)
        coefficient = self._fit_scalar_coefficient(x_values, times)
        predicted_times = [ coefficient * x for x in x_values ]
        error = self._mean_squared_error(times, predicted_times)

        return ModelFitResult(
            model_name = model.name,
            coefficient = coefficient,
            error = error,
            predicted_times = predicted_times,
        )

    @staticmethod
    def _fit_scalar_coefficient( x_values: list[ float ], y_values: list[ float ] ) -> float :
        """Compute a = sum(x*y) / sum(x*x)"""
        numerator = 0.0
        denominator = 0.0
        for x, y in zip(x_values, y_values) :
            numerator += x * y
            denominator += x * x

        if denominator == 0.0 :
            return 0.0
        return numerator / denominator

    @staticmethod
    def _mean_squared_error( observed: list[ float ], predicted: list[ float ] ) -> float :
        """Compute mean squared error"""
        total = 0.0
        for obs, pred in zip(observed, predicted) :
            diff = obs - pred
            total += diff * diff
        return total / len(observed)
