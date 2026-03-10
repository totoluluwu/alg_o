from ..analysis import AnalysisResult
from ..benchmark import BenchmarkResult
from ..exception import AlgOError
from ..regression import RegressionResult


class ComplexityPlotter :
    """Simple plotting utility for benchmark, regression, and analysis results"""

    def plot_benchmark( self, result: BenchmarkResult ) -> None :
        """Plot benchmark average times by input size"""
        plt = self._get_pyplot()
        sizes = result.sizes
        times = result.average_times
        self._validate_points(sizes, times, "benchmark")

        plt.figure()
        self._plot_measured_curve(plt, sizes, times, "Measured")
        plt.title("Benchmark Results")
        plt.xlabel("Input size")
        plt.ylabel("Average execution time (s)")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_regression( self, result: RegressionResult ) -> None :
        """Plot observed times and best-fit predicted curve"""
        plt = self._get_pyplot()
        sizes = result.sizes
        observed_times = result.observed_times
        predicted_times = result.best_fit.predicted_times

        self._validate_points(sizes, observed_times, "regression observed")
        self._validate_points(sizes, predicted_times, "regression predicted")

        plt.figure()
        self._plot_measured_curve(plt, sizes, observed_times, "Observed")
        self._plot_predicted_curve(
            plt,
            sizes,
            predicted_times,
            f"Predicted ({result.best_fit.model_name})",
        )
        plt.title(f"Regression Results - Best fit: {result.best_fit.model_name}")
        plt.xlabel("Input size")
        plt.ylabel("Execution time (s)")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_analysis( self, result: AnalysisResult ) -> None :
        """Plot measured benchmark curve and best-fit predicted curve"""
        plt = self._get_pyplot()
        sizes = result.benchmark_result.sizes
        measured_times = result.benchmark_result.average_times
        predicted_times = result.regression_result.best_fit.predicted_times

        self._validate_points(sizes, measured_times, "analysis measured")
        self._validate_points(sizes, predicted_times, "analysis predicted")

        plt.figure()
        self._plot_measured_curve(plt, sizes, measured_times, "Measured")
        self._plot_predicted_curve(plt, sizes, predicted_times, "Predicted")
        plt.title(
            f"{result.function_name} - inferred complexity: {result.best_complexity}",
        )
        plt.xlabel("Input size")
        plt.ylabel("Execution time (s)")
        plt.grid(True)
        plt.legend()
        plt.show()

    @staticmethod
    def _validate_points(
            sizes: list[ int ],
            times: list[ float ],
            label: str,
    ) -> None :
        """Validate plot input data"""
        if not sizes or not times :
            raise ValueError(f"No data to plot for {label}")
        if len(sizes) != len(times) :
            raise ValueError(f"Inconsistent data lengths for {label}")

    @staticmethod
    def _plot_measured_curve(
            plt: object,
            sizes: list[ int ],
            times: list[ float ],
            label: str,
    ) -> None :
        """Plot measured points"""
        plt.plot(sizes, times, marker = "o", label = label)

    @staticmethod
    def _plot_predicted_curve(
            plt: object,
            sizes: list[ int ],
            times: list[ float ],
            label: str,
    ) -> None :
        """Plot predicted curve"""
        plt.plot(sizes, times, marker = "x", linestyle = "--", label = label)

    @staticmethod
    def _get_pyplot() -> object :
        """Return matplotlib pyplot module"""
        try :
            import matplotlib.pyplot as plt
        except ModuleNotFoundError as exc :
            raise AlgOError("matplotlib is required for plotting") from exc
        return plt
