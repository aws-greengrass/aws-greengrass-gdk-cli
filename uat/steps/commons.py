import os

from behave import step
from pathlib import Path


@step('we change directory to {dir_name}')
def change_work_dir(context, dir_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    new_dir = Path(cwd).joinpath(dir_name)
    assert new_dir.exists(), f"Directory {dir_name} does not exist in {cwd}"
    os.chdir(str(new_dir))
    context.cwd = os.getcwd()

