from dataclasses import dataclass
from typing import List

from autofarm.jobserver import ExecInvocationParam
from autofarm.models import OffloadCommandBuilder


@dataclass
class SingleRedirectCommandBuilder(OffloadCommandBuilder):
    """
    Takes all incoming commands and prepends a fixed command list.
    E.g. with prepend command "echo":
    g++ ... -> echo g++
    """
    redirect_command: List[str]

    def build_command(self, request: ExecInvocationParam):
        return ExecInvocationParam(
            self.redirect_command[0],
            self.redirect_command + request.arguments,
            request.environment
        )