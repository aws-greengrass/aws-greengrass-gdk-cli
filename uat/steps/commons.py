from behave import given, step


@step('we change directory to {dir_name}')
def change_work_dir(context, dir_name):
    cwd = Path(context.cwd or os.getcwd())
    new_dir = cwd.joinpath(dir_name)
    assert new_dir.exists(), f"Directory {dir_name} does not exist in {cwd}"
    os.chdir(str(new_dir))
    context.cwd = os.getcwd()

