from pathlib import Path


def test_init_template_non_empty_dir(gdk_cli):
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python"])
    assert check_init_template.returncode == 1
    assert "Error details: The current directory is not empty." in check_init_template.output


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
