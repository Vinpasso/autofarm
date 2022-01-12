import asyncio

from autofarm.jobserver import JobServer, ExecInvocationParam
from autofarm.models import OffloadCommandBuilder
from autofarm.offload_command_builder.default import SingleRedirectCommandBuilder


class TestJobServer:
    offload_command_builder: OffloadCommandBuilder

    def setup(self):
        self.offload_command_builder = SingleRedirectCommandBuilder(['OFFLOAD-COMMAND', 'OFFLOAD-PARAM'])
        self.server = JobServer(
            self.offload_command_builder,
            'TARGET-.*'
        )

    def test_command_offloaded(self):
        # First offload command
        request = ExecInvocationParam(
            "TARGET-COMMAND",
            ["TARGET-COMMAND", "TARGET-PARAM"],
            []
        )

        result = self.server.offload_request(request)

        # We want the offload command to show up. Also needs to be the first argument.
        assert result.command == 'OFFLOAD-COMMAND'
        assert result.arguments == ['OFFLOAD-COMMAND', "OFFLOAD-PARAM", "TARGET-COMMAND", "TARGET-PARAM"]
        # Environment should be unchanged.
        assert result.environment == request.environment

    def test_filter_command(self):
        request = ExecInvocationParam(
            # The abspath should not affect offloading, only the command line parameters should influence filtering.
            "TARGET-COMMAND",
            ["HOST-COMMAND", "HOST-ARG"],
            []
        )

        result = self.server.offload_request(request)

        # Should not be modified because it is filtered.
        assert request == result

    async def submit_request(self, request: str, host='127.0.0.1', port=6754):
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(request)

        result = await reader.readuntil('\0')

        writer.close()
        return result

    def test_simple_request(self):
        # Have an encoded command that is independent of code changes on this side of the project
        request = '{"command": "TARGET-COMMAND", "arguments": ["TARGET-COMMAND", "TARGET-PARAM"], "environment": []}'

        event_loop = asyncio.get_event_loop()

        start_server_task = event_loop.create_task(self.server.start_server('127.0.0.1', 6754))
        event_loop.run_until_complete(start_server_task)

        run_server_task = event_loop.create_task(self.server.run_server())
        submit_request_task = event_loop.create_task(self.submit_request(request))
        done, pending = event_loop.run_until_complete(
            asyncio.wait([run_server_task, submit_request_task], return_when=asyncio.FIRST_COMPLETED)
        )
