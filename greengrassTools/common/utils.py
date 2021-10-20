from pathlib import Path

def get_static_file_path(file_name):
    """
    Returns the path of the file assuming that is in static directory. Note that this doesnt validate if path is correct
    :param file_name: name of the file
    :return: Path of the file
    """
    return Path(".").joinpath('greengrassTools/static').joinpath(file_name).resolve()