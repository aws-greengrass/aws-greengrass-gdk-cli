import os
from behave import step
from pathlib import Path
from constants import GDK_TEST_DIR


@step("we verify gdk test files")
def verify_test_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GDK_TEST_DIR).resolve().exists(), f"{GDK_TEST_DIR} does not exist"


@step("we verify that the OTF version used is {version}")
def verify_test_framework_version(context, version):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    build_system_file = Path(cwd).joinpath(GDK_TEST_DIR, "pom.xml")

    with open(build_system_file, "r") as f:
        content = f.read()
        assert f"<otf.version>{version}</otf.version>" in content, f"OTF version {version} is not used."
