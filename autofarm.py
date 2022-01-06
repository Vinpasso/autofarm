from os import environ
from pathlib import Path

from src.py.autofarm import run_autofarm

if __name__ == '__main__':
    autofarm_root = Path(__file__).parent.absolute()

    current_pythonpath = environ.get("PYTHONPATH")
    if current_pythonpath is None:
        current_pythonpath = f"{autofarm_root}"
    else:
        current_pythonpath = f"{current_pythonpath}:{autofarm_root}"
    environ["PYTHONPATH"] = current_pythonpath

    run_autofarm(str(autofarm_root))
