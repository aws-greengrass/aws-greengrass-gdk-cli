import glob
import logging
import shutil
import os
from pathlib import Path

import requests
from packaging.version import Version

import gdk
import gdk._version as version
from gdk.common.consts import MAX_RECIPE_FILE_SIZE_BYTES


class Error(OSError):
    pass


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
    logging.debug("Checking if the directory '{}' exists and is empty.".format(dir_path.resolve()))
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


def get_current_directory() -> Path:
    return Path(".").resolve()


def is_recipe_size_valid(file_path):
    file_size = Path(file_path).stat().st_size
    return file_size <= MAX_RECIPE_FILE_SIZE_BYTES, file_size


def generate_ignore_list_from_globs(root_directory, globs):
    ignored_pathnames = set()
    for pattern in globs:
        glob_pattern_whole = f"{root_directory}/{pattern}"
        ignored_pathnames = ignored_pathnames|set(glob.glob(glob_pattern_whole, recursive=True))
    return ignored_pathnames


def custom_copytree(src, dst, symlinks=False, excluded_pathnames=None, copy_function=shutil.copy2,
                    ignore_dangling_symlinks=False, dirs_exist_ok=False):
    """
    Modified version of shutil's copytree implementation allowing us to ignore with a more complex list of glob
    patterns including directories. Instead of seeing if just file names match a globlike pattern, check if the whole
    path matches a pre-filtered list of unwanted paths.

    For original implementation reference: https://github.com/python/cpython/blob/3.8/Lib/shutil.py#L516
    """
    with os.scandir(src) as itr:
        entries = list(itr)

    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_srcentry = copy_function is shutil.copy2 or copy_function is shutil.copy

    for srcentry in entries:
        if srcentry.path in excluded_pathnames:
            logging.debug("Found path to be excluded from build: " + srcentry.path)
            continue
        elif srcentry.is_dir and f"{srcentry.path}/" in excluded_pathnames:
            # Edge case where we provide a glob ending in / so glob.glob returns a directory path ending in /.
            logging.debug("Found path to be excluded from build: " + srcentry.path)
            continue
        srcname = os.path.join(src, srcentry.name)
        dstname = os.path.join(dst, srcentry.name)
        srcobj = srcentry if use_srcentry else srcname
        try:
            is_symlink = srcentry.is_symlink()
            if is_symlink and os.name == 'nt':
                # Special check for directory junctions, which appear as
                # symlinks but we want to recurse.
                lstat = srcentry.stat(follow_symlinks=False)
                if lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    is_symlink = False
            if is_symlink:
                linkto = os.readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    shutil.copystat(srcobj, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occur. copy2 will raise an error
                    if srcentry.is_dir():
                        custom_copytree(srcobj, dstname, symlinks, excluded_pathnames,
                                        copy_function, ignore_dangling_symlinks,
                                        dirs_exist_ok)
                    else:
                        copy_function(srcobj, dstname)
            elif srcentry.is_dir():
                custom_copytree(srcobj, dstname, symlinks, excluded_pathnames, copy_function,
                                ignore_dangling_symlinks, dirs_exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcobj, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)
    return dst


error_line = "\n=============================== ERROR ===============================\n"
help_line = "\n=============================== HELP ===============================\n"
current_directory = Path(".").resolve()
doc_link_device_role = "https://docs.aws.amazon.com/greengrass/v2/developerguide/device-service-role.html"
cli_version = version.__version__
latest_cli_version_file = "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-gdk-cli/main/gdk/_version.py"
s3_prefix = "s3://"

