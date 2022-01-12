from dataclasses import dataclass

from typing import List


class CorruptEnvironmentError(RuntimeError):
    """
    Raised when getting or modifying environment encounters invalid environment variables.
    """
    pass


class EnvironmentVariableNotFoundError(RuntimeError):
    """
    Raised when an environment variable is not found.
    """
    pass


@dataclass
class ExecInvocationParam:
    """
    Contains the arguments to an invocation of one of the 'exec' family of functions in libc.
    """
    command: str
    arguments: List[str]
    environment: List[str]

    def getenv(self, name: str):
        if '=' in name:
            # Cannot look up an environment variable name that is not allowed
            raise ValueError(f"Cannot load an environment variable that contains '=': '{name}'")
        if name in self.environment:
            # Environment contains variable but is missing the mandatory separator "="
            raise CorruptEnvironmentError(
                f'Environment variable "{name}" defined, but does not contain "=". '
                f'Your environment appears to be corrupt.'
            )

        # Fetch matching variables
        variables = [declaration for declaration in self.environment if declaration.startswith(f'{name}=')]
        try:
            # Try to unpack exactly one value
            [variable] = variables
        except ValueError as e:
            if len(variables) == 0:
                raise EnvironmentVariableNotFoundError(f"Environment variable '{name}' not found.") from e
            raise CorruptEnvironmentError(
                f"Environment variable '{name}' defined {len(variables)} times. Your environment appears to be corrupt."
            ) from e

        # Split into name, value
        [_, value] = variable.split('=', 1)

        return value


class OffloadCommandBuilder:
    """
    Class that manages offloading of a command. Requests contain an executable path, arguments, and an environment
    which can be rewritten before it is returned to the client.
    """

    def build_command(self, request: ExecInvocationParam):
        """
        Handle a request to run an exec function. The parameters can be modified before they are passed on to libc.
        :param request: The original parameters passed to the libc exec function.
        :return: The modified parameters to actually call exec with.
        """
        raise NotImplementedError()
