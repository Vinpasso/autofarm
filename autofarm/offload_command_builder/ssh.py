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
