import pytest

from autofarm.models import ExecInvocationParam, EnvironmentVariableNotFoundError
from autofarm.offload_command_builder.ssh import SSHCommandBuilder


def test_ssh_command_builder():
    builder = SSHCommandBuilder(
        'ssh', ['host-1', 'host-2'], False
    )

    # First offload to host 1
    environment = ["PWD=/tmp/doesn-not-exist"]
    result = builder.build_command(ExecInvocationParam(
        'echo', ['echo', 'arg'], environment.copy()
    ))

    assert result.command == "ssh"
    # First part should be offloading
    assert result.arguments[0:2] == ["ssh", "host-1"]
    # Second part is a remote host command that should contain exec echo arg
    assert "exec echo arg" in result.arguments[2]
    assert result.environment == environment

    # Second offload to host 2
    result = builder.build_command(ExecInvocationParam(
        'echo', ['echo', 'arg'], environment
    ))
    assert result.arguments[1] == "host-2"

    # Back to host 1 (round-robin)
    result = builder.build_command(ExecInvocationParam(
        'echo', ['echo', 'arg'], environment
    ))
    assert result.arguments[1] == "host-1"

    # Make sure that we fail nicely when there is no PWD variable
    environment = []
    with pytest.raises(EnvironmentVariableNotFoundError):
        builder.build_command(ExecInvocationParam(
            'echo', ['echo', 'arg'], environment.copy()
        ))

    # Make sure we don't fail when we ignore working directory.
    builder = SSHCommandBuilder(
        'ssh', ['host-1', 'host-2'], True
    )

    builder.build_command(ExecInvocationParam(
        'echo', ['echo', 'arg'], []
    ))
