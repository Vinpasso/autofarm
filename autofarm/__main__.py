import argparse
import asyncio
import base64
import sys
from argparse import ArgumentParser
from pathlib import Path

from autofarm.jobserver import JobServer
from autofarm.offload_command_builder.default import RegexRedirectCommandBuilder, get_rewrite_subcommand
from autofarm.offload_command_builder.ssh import SSHCommandBuilder, get_ssh_subcommand
from autofarm.run_subprocess import run_autofarm_invocation


class AcceptSingleValueAction(argparse.Action):
    def __init__(self, option_strings, **kwargs):
        super().__init__(option_strings, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values != "run":
            parser.error(f'Argument {values} not understood. Should be "run"')


def run_autofarm(autofarm_root: Path):
    args = do_argparse(sys.argv)

    offload_command_builder = args.offload_command_builder(args)
    server = JobServer(offload_command_builder, args.filter)

    event_loop = asyncio.get_event_loop()

    bind_address = args.jobserver_address
    bind_port = args.jobserver_port

    start_server_task = event_loop.create_task(server.start_server(bind_address, bind_port))
    event_loop.run_until_complete(start_server_task)

    run_server_task = event_loop.create_task(server.run_server())
    run_program_task = event_loop.create_task(
        run_autofarm_invocation(autofarm_root, args.program, args.args, bind_address, bind_port))
    done, pending = event_loop.run_until_complete(
        asyncio.wait([run_server_task, run_program_task], return_when=asyncio.FIRST_COMPLETED))

    for task in done:
        if task.exception():
            print(f"[AutoFarm] Error: {task.exception()}")

    for task in pending:
        task.cancel()


def do_argparse(arguments, **kwargs):
    parser = create_argument_parser(**kwargs)
    invocation = arguments[1:]
    try:
        run_index = invocation.index('run')
        # Convert arguments to base64 so the argument parser doesn't complain if an argument starts with a dash.
        # Pretty dumb but better than slicing everywhere
        invocation = invocation[0:run_index + 2] \
                     + list(map(lambda x: base64.b64encode(x.encode()).decode(), invocation[run_index + 2:]))
    except ValueError:
        # Argument run is missing. Let the argument parser handle that.
        pass
    except IndexError:
        # The program argument after run is missing. Also let argument parser handle that
        pass

    args = parser.parse_args(invocation)

    # Convert suppressed base64 arguments back to normal form.
    program_arguments = getattr(args, 'arguments')

    setattr(args, 'arguments', [base64.b64decode(value).decode() for value in program_arguments])
    return args


def create_argument_parser(parser_base=ArgumentParser):
    parser = parser_base(
        prog="autofarm", description="Easy dynamic process invocation rewriting and offloading to other machines.",
    )
    parser.add_argument(
        '--jobserver-address', metavar='Address', type=str, default='0.0.0.0',
        help='Interface address on which to run the jobserver and listen for offloading requests.'
    )
    parser.add_argument(
        '--jobserver-port', metavar='Port', type=int, default=6754,
        help='TCP port number on which the jobserver listens.'
    )
    parser.add_argument(
        '--filter', type=str, default=".*",
        help='Filter which commands will be rewritten. For non matching commands, the rewrite step will be skipped. '
             'Uses regular expression syntax and partial matches are accepted.'
    )

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        'run', action=AcceptSingleValueAction,
        help=""
    )
    parent_parser.add_argument(
        'program', type=str,
        help="The program that AutoFarm should invoke."
    )
    parent_parser.add_argument(
        'arguments', nargs='*', default=[],
        help="A list of arguments forwarded to the program."
    )

    subparsers = parser.add_subparsers(
        metavar='rewriter',
        required=True,
        help='Specify one of the following invocation rewriters to use. '
             'Use autofarm [rewriter] --help for details on each rewriter.'
    )
    get_rewrite_subcommand(subparsers, parent_parser)
    get_ssh_subcommand(subparsers, parent_parser)
    return parser


if __name__ == '__main__':
    run_autofarm(Path(__file__).parent)
