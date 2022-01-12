import pytest

from autofarm.models import ExecInvocationParam, CorruptEnvironmentError, EnvironmentVariableNotFoundError


def test_getenv():
    test_invocation = ExecInvocationParam(
        '',
        [],
        ["REGULAR_VAR=/test/", "VAR_EMPTY_VALUE="]
    )

    # Test normal variable, empty variable, missing variable
    assert test_invocation.getenv('REGULAR_VAR') == "/test/"
    assert test_invocation.getenv('VAR_EMPTY_VALUE') == ""

    with pytest.raises(EnvironmentVariableNotFoundError):
        test_invocation.getenv('NON_EXISTENT_VARIABLE')

    # Test some corrupt environments
    test_invocation = ExecInvocationParam(
        '',
        [],
        ["VAR_WITHOUT_EQUALS_SIGN", "DOUBLE_DEFINED_VAR=", "DOUBLE_DEFINED_VAR="]
    )

    with pytest.raises(CorruptEnvironmentError):
        test_invocation.getenv('VAR_WITHOUT_EQUALS_SIGN')

    with pytest.raises(CorruptEnvironmentError):
        test_invocation.getenv('DOUBLE_DEFINED_VAR')

    # Test some faulty invocations
    with pytest.raises(ValueError):
        test_invocation.getenv('VAR=NAME=WITH=EQUALS=SIGN')

    with pytest.raises(EnvironmentVariableNotFoundError):
        test_invocation.getenv('')
