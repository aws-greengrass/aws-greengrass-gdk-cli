from pathlib import Path
import greengrassTools

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

    if file_path.exists():
        return file_path
    else:
        return None

def is_directory_empty(dir_path):
    """
    Checks if the given directory path is empty.

    Parameters
    ----------
        dir_path(string): Directory path to check.

    Returns
    -------
        (bool): True if the directory exists and is empty. False if directory doesn't exist or not empty.
    """
    dir_path = Path(dir_path).resolve()
    if dir_path.is_dir() and not list(dir_path.iterdir()):
        return True
    else:    
        return False