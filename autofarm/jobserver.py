import asyncio
import json
import re
import shlex
import sys
from asyncio import StreamReader, StreamWriter, AbstractServer, IncompleteReadError
from dataclasses import dataclass

from autofarm.models import ExecInvocationParam
from autofarm.offload_command_builder.default import OffloadCommandBuilder


@dataclass
class JobServer:
    offload_command_builder: OffloadCommandBuilder
    offload_regex_filter: str

    _server: AbstractServer = None

    def offload_request(self, request: ExecInvocationParam):
        shell_command = shlex.join(request.arguments)
        if not re.search(self.offload_regex_filter, shell_command):
            print(f"[AutoFarm] Ignore {' '.join(request.arguments)}")
            return request

        reforge_result = self.offload_command_builder.build_command(request)
        print(f"[AutoFarm] Offloading: {shell_command}", file=sys.stderr)
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
