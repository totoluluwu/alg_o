import pathlib
import random
import sys

import pytest


ROOT_DIR = pathlib.Path(__file__).resolve().parents[ 2 ]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path :
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(autouse = True)
def _set_random_seed() -> None :
    random.seed(2026)
