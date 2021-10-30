from pathlib import Path
import greengrassTools
import shutil
import logging 

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
    greengrassTools_module_dir = Path(greengrassTools.__file__).resolve().parent
    file_path = greengrassTools_module_dir.joinpath('static').joinpath(file_name).resolve()

    if file_exists(file_path):
        return file_path
    else:
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
    fp = Path(file_path).resolve()
    return fp.is_file()

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
    else:    
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

line = "\n------------------------------------------------------------------------\n"
current_directory = Path('.').resolve()
log_format = "[%(asctime)s] %(levelname)s - %(message)s"