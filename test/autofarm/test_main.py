import argparse

import pytest

from autofarm.__main__ import do_argparse
from autofarm.offload_command_builder.default import RegexRedirectCommandBuilder


class ErrorCatchingArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if status:
            raise argparse.ArgumentError(None, f'Exiting because of an error: {message}')
        exit(status)


def test_argparse():

    # Can have invoked program and argument
    result = do_argparse(['autofarm', 'rewrite', 'run', 'echo', 'test'], parser_base=ErrorCatchingArgumentParser)
    assert result.program == 'echo'
    assert result.arguments == ['test']
    assert isinstance(result.offload_command_builder(result), RegexRedirectCommandBuilder)

    # Can have invoked program with option arguments
    result = do_argparse(['autofarm', 'rewrite', 'run', 'echo', '--test', '--test2'], parser_base=ErrorCatchingArgumentParser)
    assert result.program == 'echo'
    assert result.arguments == ['--test', '--test2']

    # Can have invoked program without options
    result = do_argparse(['autofarm', 'rewrite', 'run', 'echo'], parser_base=ErrorCatchingArgumentParser)
    assert result.program == 'echo'
    assert result.arguments == []

    # Unknown option detected
    with pytest.raises(argparse.ArgumentError):
        do_argparse(["autofarm", '--non-existent', 'rewrite', 'run', 'echo'], parser_base=ErrorCatchingArgumentParser)

    with pytest.raises(argparse.ArgumentError):
        # Unknown option in subparser detected
        do_argparse(["autofarm", 'rewrite', '--non-existent', 'run', 'echo'], parser_base=ErrorCatchingArgumentParser)

    with pytest.raises(argparse.ArgumentError):
        # Missing run command
        do_argparse(["autofarm", 'rewrite'], parser_base=ErrorCatchingArgumentParser)

    with pytest.raises(argparse.ArgumentError):
        # Missing program
        do_argparse(["autofarm", 'rewrite', 'run'], parser_base=ErrorCatchingArgumentParser)

