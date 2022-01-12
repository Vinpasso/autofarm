import os
from pathlib import Path

from autofarm.subprocess import create_environment


def test_environment_variables():
    os.environ["TEST_VAR"] = "TEST"
    environment = create_environment(Path(__file__), "HOST", 1234)
    assert environment["LD_PRELOAD"].endswith('libautofarm_intercept.so')
    assert environment["AUTOFARM_JOBSERVER_HOST"] == "HOST"
    assert environment["TEST_VAR"] == "TEST"
