"""Data structures representing regression outcomes"""

from dataclasses import dataclass


@dataclass(frozen = True)
class ModelFitResult :
    """Fit result for one model"""

    model_name: str
    coefficient: float
    error: float
    predicted_times: list[ float ]


@dataclass(frozen = True)
class RegressionResult :
    """Global regression result"""

    sizes: list[ int ]
    observed_times: list[ float ]
    model_fits: list[ ModelFitResult ]
    best_fit: ModelFitResult

    def get_fit( self, model_name: str ) -> ModelFitResult | None :
        """Return one model fit by name"""
        for fit in self.model_fits :
            if fit.model_name == model_name :
                return fit
        return None
