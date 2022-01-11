import asyncio
from os import environ
from pathlib import Path
from typing import List


async def run_autofarm_invocation(autofarm_root: Path, cmd: str, args: List[str], jobserver_host: str, jobserver_port: int):
    prepared_env = environ.copy()
    if prepared_env.get("LD_PRELOAD") is not None:
        raise RuntimeError("AutoFarm has detected that a LD_PRELOAD library is already set. AutoFarm cannot work "
                           "without LD_PRELOAD support. Please remove the preloaded library.")
    prepared_env["LD_PRELOAD"] = f'{autofarm_root.joinpath("libautofarm_intercept.so").absolute()}'
    prepared_env["AUTOFARM_JOBSERVER_HOST"] = jobserver_host
    prepared_env["AUTOFARM_JOBSERVER_PORT"] = str(jobserver_port)

    proc = await asyncio.create_subprocess_exec(
        cmd,
        *args,
        env=prepared_env
    )

    await proc.communicate()
    return proc.returncode