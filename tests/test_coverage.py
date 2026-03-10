import ast
import io
import pathlib
import sys
import trace
import unittest


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 1 ]
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"

if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))


class SourceCoverageTests(unittest.TestCase) :

    def test_source_coverage_is_above_90( self ) -> None :
        tracer = trace.Trace(count = True, trace = False)

        def run_inner_suite() -> tuple[ unittest.result.TestResult, str ] :
            stream = io.StringIO()
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            suite.addTests(
                loader.discover(
                    start_dir = str(TESTS_DIR),
                    pattern = "test_regression.py",
                ),
            )
            suite.addTests(
                loader.discover(
                    start_dir = str(TESTS_DIR),
                    pattern = "test_generation.py",
                ),
            )
            suite.addTests(
                loader.discover(
                    start_dir = str(TESTS_DIR),
                    pattern = "test_benchmark.py",
                ),
            )
            suite.addTests(
                loader.discover(
                    start_dir = str(TESTS_DIR),
                    pattern = "test_exception.py",
                ),
            )
            runner = unittest.TextTestRunner(stream = stream, verbosity = 0)
            result = runner.run(suite)
            return result, stream.getvalue()

        self._clear_modules("test_regression")
        self._clear_modules("test_generation")
        self._clear_modules("test_benchmark")
        self._clear_modules("test_exception")
        self._clear_modules("alg_o")
        inner_result, inner_output = tracer.runfunc(run_inner_suite)
        self.assertTrue(
            inner_result.wasSuccessful(),
            msg = "Inner test suite failed\n" + inner_output,
        )

        traced_counts = tracer.results().counts

        total_statements = 0
        executed_statements = 0

        for file_path in sorted(SRC_DIR.rglob("*.py")) :
            statement_lines = self._statement_lines(file_path)
            total_statements += len(statement_lines)

            executed_lines_in_file = {
                line_no
                for (filename, line_no), hit_count in traced_counts.items()
                if hit_count > 0
                   and pathlib.Path(filename).resolve() == file_path.resolve()
                   and line_no in statement_lines
            }
            executed_statements += len(executed_lines_in_file)

        coverage = (
            100.0 * executed_statements / total_statements
            if total_statements > 0
            else 100.0
        )

        print(f"Source coverage: {coverage:.2f}%")
        self.assertGreaterEqual(
            coverage,
            90.0,
            msg = f"Source coverage is below threshold: {coverage:.2f}% < 90%",
        )

    @staticmethod
    def _statement_lines( file_path: pathlib.Path ) -> set[ int ] :
        source = file_path.read_text(encoding = "utf-8")
        syntax_tree = ast.parse(source, filename = str(file_path))
        return {
            node.lineno
            for node in ast.walk(syntax_tree)
            if isinstance(node, ast.stmt)
        }

    @staticmethod
    def _clear_modules( prefix: str ) -> None :
        module_names = [ name for name in sys.modules if
                         name == prefix or name.startswith(prefix + ".") ]
        for name in module_names :
            del sys.modules[ name ]


if __name__ == "__main__" :
    unittest.main()
