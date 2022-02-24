from pathlib import Path


def test_init_template_non_empty_dir(gdk_cli):
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python"])
    assert check_init_template.returncode == 1
    assert "Try `gdk component init --help`" in check_init_template.output


def test_init_template(change_test_dir, gdk_cli):
    dirpath = Path(change_test_dir)
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python"])
    assert check_init_template.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").resolve().exists()
    assert Path(dirpath).joinpath("gdk-config.json").resolve().exists()


def test_init_template_with_new_directory(change_test_dir, gdk_cli):
    dir = "test-dir"
    dirpath = Path(change_test_dir).joinpath(dir)
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python", "-n", dir])
    assert check_init_template.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").resolve().exists()
    assert Path(dirpath).joinpath("gdk-config.json").resolve().exists()


def test_init_repository(change_test_dir, gdk_cli):
    dirpath = Path(change_test_dir)
    check_init_repo = gdk_cli.run(["component", "init", "-r", "aws-greengrass-labs-database-influxdb"])
    assert check_init_repo.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").exists()
    assert Path(dirpath).joinpath("gdk-config.json").exists()


def test_init_repository_with_new_dir(change_test_dir, gdk_cli):
    dir = "test-dir"
    dirpath = Path(change_test_dir).joinpath(dir)
    check_init_repo = gdk_cli.run(["component", "init", "-r", "aws-greengrass-labs-database-influxdb", "-n", dir])
    assert check_init_repo.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").exists()
    assert Path(dirpath).joinpath("gdk-config.json").exists()


def test_init_repository_not_exists(change_test_dir, gdk_cli):
    check_init_repo = gdk_cli.run(["component", "init", "-r", "repo-not-exists"])
    assert check_init_repo.returncode == 1
    assert (
        "Could not find the component repository 'repo-not-exists' in Greengrass Software Catalog." in check_init_repo.output
    )


def test_init_template_not_exists(change_test_dir, gdk_cli):
    check_init_temp = gdk_cli.run(["component", "init", "-t", "temp-not-exists", "-l", "python"])
    assert check_init_temp.returncode == 1
    assert (
        "Could not find the component template 'temp-not-exists-python' in Greengrass Software Catalog."
        in check_init_temp.output
    )


def test_init_incomplete_args(change_test_dir, gdk_cli):
    check_init = gdk_cli.run(["component", "init"])
    assert check_init.returncode == 1
    assert "Could not initialize the project as the arguments passed are invalid." in check_init.output
