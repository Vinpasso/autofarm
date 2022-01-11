import asyncio
import json
import re
import shlex
import sys
from asyncio import StreamReader, StreamWriter, AbstractServer, IncompleteReadError
from typing import List

from dataclasses import dataclass


@dataclass
class ExecInvocationParam:
    command: str
    arguments: List[str]
    environment: List[str]

    # TODO: BAD
    def getenv(self, name: str):
        return [value for key, value in map(lambda x: x.split('=', 1), self.environment) if key == name][0]


@dataclass
class JobServer:
    remote_invocation_command: str
    remote_invocation_hosts: List[str]
    remote_invocation_skip_directory_change: bool
    offload_regex_filter: str

    _server: AbstractServer = None
    _remote_host_index = 0

    def build_remote_command(self, request):
        remote_command = ""
        if not self.remote_invocation_skip_directory_change:
            remote_command += f'cd {request.getenv("PWD")} && '
        remote_command += f'exec {shlex.join(request.arguments)}'
        return remote_command

    def offload_request(self, request: ExecInvocationParam):
        if not re.search(self.offload_regex_filter, request.command):
            print(f"[AutoFarm] Ignore {' '.join(request.arguments)}")
            return request

        remote_command = self.build_remote_command(request)
        reforge_result = ExecInvocationParam(
            self.remote_invocation_command,
            [self.remote_invocation_command,
             self.remote_invocation_hosts[self._remote_host_index],
             remote_command],
            request.environment
        )
        print(f"[AutoFarm] Offloading: {shlex.join(reforge_result.arguments)}", file=sys.stderr)
        self._remote_host_index = (self._remote_host_index + 1) % len(self.remote_invocation_hosts)
        return reforge_result

    async def handle_client(self, read_channel: StreamReader, write_channel: StreamWriter):
        try:
            request_str = await read_channel.readuntil(b'\0')
            request = json.loads(request_str[0:len(request_str)-1], object_hook=lambda o: ExecInvocationParam(**o))
            response = self.offload_request(request)
            response_str = json.dumps(response.__dict__)
            write_channel.write((response_str).encode('utf-8'))
            write_channel.write(b'\0')
            await write_channel.drain()
        except IncompleteReadError as e:
            print(f'[AutoFarm] Socket closed: {e}')

    async def start_server(self, bind_address: str, bind_port: int):
        self._server = await asyncio.start_server(self.handle_client, bind_address, bind_port)
        print(f'[AutoFarm] Started jobserver on {bind_address}:{bind_port}')

    async def run_server(self):
        async with self._server:
            await self._server.serve_forever()
