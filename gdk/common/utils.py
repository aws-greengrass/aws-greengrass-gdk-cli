import logging
import shutil
from pathlib import Path

import requests
from packaging.version import Version

import gdk
import gdk._version as version


def get_static_file_path(file_name):
    """
    Returns the path of the file assuming that is in static directory.

    Parameters
    ----------
        file_name(string): Name of the file in static folder.

    Returns
    -------
        file_path(Path): Returns absolute path of the file if it exists. Else None
    """
    gdk_module_dir = Path(gdk.__file__).resolve().parent
    file_path = gdk_module_dir.joinpath("static").joinpath(file_name).resolve()

    if file_exists(file_path):
        return file_path
    return None


def file_exists(file_path):
    """
    Checks if the given path exists and is a file.

    Parameters
    ----------
        file_path(Path): File path to check.

    Returns
    -------
        (bool): True if the file exists. False if the given path doesn't exist or is not a file.
    """
    logging.debug("Checking if the file '{}' exists.".format(file_path.resolve()))
    # Compatible with < py 3.8
    try:
        return Path(file_path).resolve().is_file()
    except Exception as e:
        logging.debug(e)
        return False


def dir_exists(dir_path):
    """
    Checks if the given path exists and is a directory.

    Parameters
    ----------
        dir_path(Path): File path to check.

    Returns
    -------
        (bool): True if the directory exists. False if the given path doesn't exist or is not a directory.
    """
    logging.debug("Checking if the directory '{}' exists.".format(dir_path.resolve()))
    dp = Path(dir_path).resolve()
    # Compatible with < py 3.8
    try:
        return dp.is_dir()
    except Exception as e:
        logging.debug(e)
        return False


def is_directory_empty(directory_path):
    """
    Checks if the given directory path is empty.

    Parameters
    ----------
        directory_path(Path): Directory path to check.

    Returns
    -------
        (bool): True if the directory exists and is empty. False if directory doesn't exist or not empty.
    """
    dir_path = Path(directory_path).resolve()
    logging.debug(
        "Checking if the directory '{}' exists and is empty.".format(dir_path.resolve())
    )
    if dir_path.is_dir() and not list(dir_path.iterdir()):
        return True
    return False


def clean_dir(dir):
    """
    Deletes the directory.

    Parameters
    ----------
        dir(Path): Path of the directory to remove.

    Returns
    -------
        None
    """
    logging.debug("Deleting the directory '{}' if it exists.".format(dir.resolve()))
    shutil.rmtree(dir, ignore_errors=True, onerror=None)


def get_latest_cli_version():
    try:
        response = requests.get(latest_cli_version_file)
        if response.status_code == 200:
            version_string = response.text.splitlines()[0]
            l_version = version_string.split("__version__ = ")[1].strip('"')
            return l_version
    except Exception as e:
        logging.debug(
            f"Fetching latest version of the cli tool failed. Proceeding with the command execution.\nError details: {e}"
        )
    return cli_version


def cli_version_check():
    latest_cli_version = get_latest_cli_version()
    update_command = f"pip3 install git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v{latest_cli_version}"
    if Version(cli_version) < Version(latest_cli_version):
        logging.info(
            f"New version of GDK CLI - {latest_cli_version} is available. Please update the cli using the command"
            f" `{update_command}`.\n"
        )


def get_next_patch_version(version_number: str) -> str:
    split_with_hyphen = version_number.split("-")
    split_with_plus = split_with_hyphen[0].split("+")
    semver_numeric = split_with_plus[0].split(".")
    major = semver_numeric[0]
    minor = semver_numeric[1]
    patch = semver_numeric[2]
    next_patch_version = int(patch) + 1
    return f"{major}.{minor}.{str(next_patch_version)}"


error_line = "\n=============================== ERROR ===============================\n"
help_line = "\n=============================== HELP ===============================\n"
current_directory = Path(".").resolve()
doc_link_device_role = (
    "https://docs.aws.amazon.com/greengrass/v2/developerguide/device-service-role.html"
)
cli_version = version.__version__
latest_cli_version_file = "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-gdk-cli/main/gdk/_version.py"
s3_prefix = "s3://"
