import os
from behave import step
from pathlib import Path
from constants import GDK_TEST_DIR, GG_BUILD_DIR


@step("we verify gdk test files")
def verify_test_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GDK_TEST_DIR).resolve().exists(), f"{GDK_TEST_DIR} does not exist"


@step("we verify that the GTF version used is {version}")
def verify_test_framework_version(context, version):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    build_system_file = Path(cwd).joinpath(GDK_TEST_DIR, "pom.xml")

    with open(build_system_file, "r") as f:
        content = f.read()
        assert f"<otf.version>{version}-SNAPSHOT</otf.version>" in content, f"GTF version {version} is not used."


@step("we verify the test build files")
def verify_test_build_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    test_build_file = Path(cwd).joinpath(GG_BUILD_DIR, GDK_TEST_DIR, "target", "uat-features-1.0.0.jar")
    test_recipe_file = Path(cwd).joinpath(GG_BUILD_DIR, "recipes", "e2e_test_recipe.yaml")

    assert test_build_file.resolve().exists(), f"{test_build_file} does not exist"
    assert test_recipe_file.resolve().exists(), f"{test_recipe_file} does not exist"
