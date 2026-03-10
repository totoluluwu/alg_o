import pathlib
import sys
import unittest


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))

from alg_o import (
    AlgOError,
    BenchmarkError,
    GenerationError,
    InvalidAnnotationError,
    RegressionError,
    UnsupportedTypeError,
)
from alg_o import exception


class ExceptionHierarchyTests(unittest.TestCase) :

    def test_hierarchy( self ) -> None :
        self.assertTrue(issubclass(AlgOError, Exception))
        self.assertTrue(issubclass(GenerationError, AlgOError))
        self.assertTrue(issubclass(UnsupportedTypeError, GenerationError))
        self.assertTrue(issubclass(InvalidAnnotationError, GenerationError))
        self.assertTrue(issubclass(BenchmarkError, AlgOError))
        self.assertTrue(issubclass(RegressionError, AlgOError))

    def test_exception_instances( self ) -> None :
        self.assertIsInstance(GenerationError("x"), AlgOError)
        self.assertIsInstance(BenchmarkError("x"), AlgOError)
        self.assertIsInstance(RegressionError("x"), AlgOError)


class ExceptionExportsTests(unittest.TestCase) :

    def test_exception_package_exports( self ) -> None :
        expected = {
            "AlgOError",
            "GenerationError",
            "UnsupportedTypeError",
            "InvalidAnnotationError",
            "BenchmarkError",
            "RegressionError",
        }
        self.assertEqual(set(exception.__all__), expected)

    def test_root_package_exports( self ) -> None :
        import alg_o

        expected = {
            "AlgOError",
            "GenerationError",
            "UnsupportedTypeError",
            "InvalidAnnotationError",
            "BenchmarkError",
            "RegressionError",
        }
        self.assertEqual(set(alg_o.__all__), expected)


if __name__ == "__main__" :
    unittest.main()
