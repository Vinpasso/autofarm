import re
import shlex
from dataclasses import dataclass
from typing import List

from autofarm.jobserver import ExecInvocationParam
from autofarm.models import OffloadCommandBuilder


@dataclass
class RegexRedirectCommandBuilder(OffloadCommandBuilder):
    """
    Takes all incoming commands and prepends a fixed command list.
    E.g. with prepend command "echo":
    g++ ... -> echo g++
    """
    find_expressions: List[str]
    replace_expressions: List[str]

    def build_command(self, request: ExecInvocationParam):
        command_line = shlex.join(request.arguments)

        if len(self.find_expressions) != len(self.replace_expressions):
            raise RuntimeError("Don't have the same number of find and replace expressions.")
        for find_expression, replace_expression in zip(self.find_expressions, self.replace_expressions):
            command_line = re.sub(find_expression, replace_expression, command_line)

        reparsed_arguments = shlex.split(command_line)
        return ExecInvocationParam(
            reparsed_arguments[0],
            reparsed_arguments,
            request.environment
        )


def create_rewrite(args):
    find_expressions = []
    replace_expressions = []

    for [find_expression, replace_expression] in args.replace:
        find_expressions.append(find_expression)
        replace_expression.append(replace_expression)

    return RegexRedirectCommandBuilder(find_expressions, replace_expressions)


def get_rewrite_subcommand(subparsers, parent):
    # Rewrite subcommand
    prefix = subparsers.add_parser(
        'rewrite', parents=[parent],
        description='Rewrite process invocations using find-replace regular expression substitution.',
        help='Rewrite process invocations using find-replace regular expression substitution.'
    )
    prefix.set_defaults(offload_command_builder=create_rewrite)
    prefix.add_argument(
        '--replace', nargs=2, action='append', default=[], metavar=('find', 'replace'),
        help="Replace all occurences of 'find' with 'replace'. "
             "Both find and replace are interpreted as regular expressions. "
             "Specify multiple times to perform multiple substitutions."
    )
