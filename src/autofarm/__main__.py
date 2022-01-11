import asyncio
from argparse import ArgumentParser
from pathlib import Path

from autofarm.jobserver import JobServer
from autofarm.subprocess import run_autofarm_invocation


def run_autofarm(autofarm_root: Path):
    parser = ArgumentParser(description="Automatically distribute a job across multiple nodes.")

    parser.add_argument('--jobserver-bind-address', type=str, default='0.0.0.0',
                        help='Interface address on which to run the jobserver and listen for offloading requests.')
    parser.add_argument('--jobserver-bind-port', type=int, default=6754,
                        help='TCP port number on which the jobserver listens.')
    parser.add_argument('--remote-shell', type=str, default="ssh",
                        help='The shell to redirect invoked commands to. Defaults to SSH. '
                             'Make sure that password-less authentication to all hosts is possible.')
    parser.add_argument('--host', action='append', default=[], required=True,
                        help='Host to offload work to. Specify multiple times to offload work in round-robin schedule.')
    parser.add_argument('--offload-regex-filter', type=str, default=".*",
                        help='Filter which applications to offload by their name using regex. Partial matches are accepted.')

    args, invocation_command = parser.parse_known_args()

    if len(invocation_command) == 0:
        print('Please specify an invocation command.')
        exit(255)

    server = JobServer(args.remote_shell, args.host, args.offload_regex_filter, args.offload_regex_filter)

    event_loop = asyncio.get_event_loop()

    bind_address = args.jobserver_bind_address
    bind_port = args.jobserver_bind_port

    start_server_task = event_loop.create_task(server.start_server(bind_address, bind_port))
    event_loop.run_until_complete(start_server_task)

    run_server_task = event_loop.create_task(server.run_server())
    run_program_task = event_loop.create_task(run_autofarm_invocation(autofarm_root, invocation_command[0], invocation_command[1:], bind_address, bind_port))
    done, pending = event_loop.run_until_complete(asyncio.wait([run_server_task, run_program_task], return_when=asyncio.FIRST_COMPLETED))

    for task in done:
        if task.exception():
            print(f"[AutoFarm] Error: {task.exception()}")

    for task in pending:
        task.cancel()


if __name__ == '__main__':
    run_autofarm(Path(__file__).parent)