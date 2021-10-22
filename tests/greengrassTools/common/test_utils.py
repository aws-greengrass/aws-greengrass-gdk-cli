from pathlib import Path
# import os 
# import greengrassTools

def test_get_static_file_path_exists(mocker):

    mock_iterdir=mocker.patch("pathlib.Path.exists", return_value=True)
    file_name=""

    file_path = Path(".")
    mock_file_path = mocker.patch("pathlib.Path.resolve", return_value=file_path)

    assert utils.get_static_file_path(file_name) == file_path

def test_get_static_file_path_not_exists(mocker):
    mock_iterdir=mocker.patch("pathlib.Path.exists", return_value=False)
    file_name=""

    file_path = Path(".")
    mock_file_path = mocker.patch("pathlib.Path.resolve", return_value=file_path)

    assert not utils.get_static_file_path(file_name)
 

import greengrassTools.common.utils as utils

def test_is_directory_empty_with_empty_dir(mocker):
    mock_is_dir=mocker.patch("pathlib.Path.is_dir", return_value=True)
    mock_iterdir=mocker.patch("pathlib.Path.iterdir", return_value=[])
    dir_path=""

    assert utils.is_directory_empty(dir_path)
    assert mock_is_dir.call_count ==1
    assert mock_iterdir.call_count ==1

def test_is_directory_empty_with_empty_but_no_dir(mocker):
    mock_is_dir=mocker.patch("pathlib.Path.is_dir", return_value=False)
    mock_iterdir=mocker.patch("pathlib.Path.iterdir", return_value=[])
    dir_path=""

    assert not utils.is_directory_empty(dir_path)
    assert mock_is_dir.call_count ==1
    assert mock_iterdir.call_count ==0

def test_is_directory_empty_with_non_empty_dir(mocker):
    mock_is_dir=mocker.patch("pathlib.Path.is_dir", return_value=True)
    mock_iterdir=mocker.patch("pathlib.Path.iterdir", return_value=[1])
    dir_path=""

    assert not utils.is_directory_empty(dir_path)
    assert mock_is_dir.call_count ==1
    assert mock_iterdir.call_count ==1
    