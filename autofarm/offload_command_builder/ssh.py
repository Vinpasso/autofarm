from typing import List

import shlex
from dataclasses import dataclass
from autofarm.jobserver import ExecInvocationParam
from autofarm.models import EnvironmentVariableNotFoundError
from autofarm.offload_command_builder.default import OffloadCommandBuilder


@dataclass
class SSHCommandBuilder(OffloadCommandBuilder):
    remote_invocation_command: str
    remote_invocation_hosts: List[str]
    remote_invocation_skip_directory_change: bool

    # Keeps track of which host in the host list is next for offloading. Is incremented before first use
    _remote_host_index = -1

    def build_remote_command(self, request):
        remote_command = ""
        if not self.remote_invocation_skip_directory_change:
            try:
                remote_command += f'cd {request.getenv("PWD")} && '
            except EnvironmentVariableNotFoundError as e:
                raise EnvironmentVariableNotFoundError(
                    'Cannot determine the current directory because $PWD is missing. '
                    'Turn on "skip directory change" if the working directory should be ignored.'
                ) from e
        remote_command += f'exec {shlex.join(request.arguments)}'
        return remote_command

    def build_command(self, request: ExecInvocationParam):
        self._remote_host_index = (self._remote_host_index + 1) % len(self.remote_invocation_hosts)
        remote_command = self.build_remote_command(request)
        return ExecInvocationParam(
            self.remote_invocation_command,
            [self.remote_invocation_command,
             self.remote_invocation_hosts[self._remote_host_index],
             remote_command],
            request.environment
        )


def create_ssh(args):
    return SSHCommandBuilder(
        args.remote_shell,
        args.host,
        args.skip_directory_change
    )


def get_ssh_subcommand(subparsers, parent):
    # SSH subcommand
    ssh_subparser = subparsers.add_parser(
        'ssh', parents=[parent],
        description="Offload process invocations to one or more remote computers.",
        help='Offload process invocations to one or more remote computers.'
    )
    ssh_subparser.set_defaults(offload_command_builder=SSHCommandBuilder)
    ssh_subparser.add_argument(
        '--remote-shell', type=str, default="ssh",
        help='The shell to redirect invoked commands to. Defaults to SSH. '
             'Make sure that password-less authentication to all hosts is possible.'
    )
    ssh_subparser.add_argument(
        '--host', action='append', default=[], required=True,
        help='Host to offload work to. Specify multiple times to offload work in round-robin schedule.'
    )
    ssh_subparser.add_argument(
        '--skip-directory-change', action='store_true',
        help='Skip the change to the current working directory on the remote host.'
    )
