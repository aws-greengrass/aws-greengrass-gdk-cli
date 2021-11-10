from pathlib import Path, PosixPath
from shutil import Error
import pytest
import json
from unittest.mock import patch,mock_open
from unittest.mock import ANY
from build.lib.greengrassTools.common import utils

from greengrassTools.common.exceptions import error_messages

valid_project_config_file=Path(".").joinpath('tests/greengrassTools/static/build_command').joinpath('valid_project_config_build.json').resolve()
json_values = {
    "component_name": "component_name",
    "component_build_config":{
        "build_system": "zip"
    },
    "component_version": "1.0.0",
    "component_author": "abc",
    "bucket": "default",
    "gg_build_directory": PosixPath("/Users/nukai/workplace/gdk/src/GDK-CLI-Internal/greengrass-build"),
    "gg_build_artifacts_dir": PosixPath("/Users/nukai/workplace/gdk/src/GDK-CLI-Internal/greengrass-build/artifacts"),
    "gg_build_recipes_dir": PosixPath("/Users/nukai/workplace/gdk/src/GDK-CLI-Internal/greengrass-build/recipes"),
    "gg_build_component_artifacts_dir": PosixPath("/Users/nukai/workplace/gdk/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"),
    "component_recipe_file": PosixPath("/Users/nukai/workplace/gdk/src/GDK-CLI-Internal/tests/greengrassTools/static/build_command/valid_component_recipe.json"),
    "parsed_component_recipe": {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {
            "DefaultConfiguration": {
                "Message": "world"
            }
        },
        "Manifests": [
            {
                "Platform": {
                    "os": "linux"
                },
                "Lifecycle": {
                    "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                },
                "Artifacts": [
                    {
                        "URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
                    }
                ]
            }
        ]
    },
}

    
with open(valid_project_config_file, 'r') as f:
    parsed_config_file = json.loads(f.read())

def test_create_recipe_file_json_valid(mocker):
    # Tests if a new recipe file is created with updated values - json
    mock_get_parsed_config= mocker.patch("greengrassTools.commands.component.project_utils.get_project_config_values", return_value=json_values)

    import greengrassTools.commands.component.build as build
    assert mock_get_parsed_config.call_count == 1
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath(json_values["component_recipe_file"].name).resolve()
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump")
    with patch("builtins.open", mock_open()) as mock_file:
        build.create_build_recipe_file()
        mock_file.assert_any_call(file_name, 'w')
        mock_json_dump.call_count ==1 
        assert not mock_yaml_dump.called

def test_create_recipe_file_yaml_valid(mocker):
    # Tests if a new recipe file is created with updated values - yaml
    # Tests if a new recipe file is created with updated values - json
    import greengrassTools.commands.component.build as build
    build.project_config["component_recipe_file"]  = Path('some-yaml.yaml').resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath(build.project_config["component_recipe_file"].resolve().name).resolve()
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump")
    with patch("builtins.open", mock_open()) as mock_file:
        build.create_build_recipe_file()
        mock_file.assert_called_once_with(file_name, 'w')
        mock_json_dump.call_count ==1 
        assert mock_yaml_dump.called

def test_create_recipe_file_json_invalid(mocker):
    # Raise exception for when creating recipe failed due to invalid json
    import greengrassTools.commands.component.build as build
    build.project_config["component_recipe_file"]  = Path('some-json.json').resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath(json_values["component_recipe_file"].name).resolve()
    def throw_error(*args, **kwargs):
        if args[0] == json_values["parsed_component_recipe"]:
            raise TypeError('I mock json error')
    mock_json_dump = mocker.patch("json.dumps", side_effect=throw_error)
    mock_yaml_dump = mocker.patch("yaml.dump")
    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            build.create_build_recipe_file()
        assert "Failed to create build recipe file at" in e.value.args[0]
        mock_file.assert_called_once_with(file_name, 'w')
        mock_json_dump.call_count ==1 
        assert not mock_yaml_dump.called

def test_create_recipe_file_yaml_invalid(mocker):
    # Raise exception for when creating recipe failed due to invalid yaml
    import greengrassTools.commands.component.build as build
    build.project_config["component_recipe_file"]  = Path('some-yaml.yaml').resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath(build.project_config["component_recipe_file"].name).resolve()
    def throw_error(*args, **kwargs):
        if args[0] == json_values["parsed_component_recipe"]:
            raise TypeError('I mock yaml error')
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump",side_effect=throw_error)
    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            build.create_build_recipe_file()
        assert "Failed to create build recipe file at" in e.value.args[0]
        mock_file.assert_called_once_with(file_name, 'w')
        mock_json_dump.call_count ==1 
        assert mock_yaml_dump.called

def test_get_build_folder_by_build_system():
    import greengrassTools.commands.component.build as build
    # build_info={
    #         "build_system": "gradle",
    #         "build_command": ["gradle","build"],
    #         "skip_tests_command": ["-x", "test"],
    #         "build_folder":["build","lib"]
    #         }
    path = build._get_build_folder_by_build_system()
    assert path.resolve() == Path('.').joinpath(*["zip-build"]).resolve()

def test_create_gg_build_directories(mocker):
    mocker.patch("greengrassTools.commands.component.project_utils.get_project_config_values", return_value=json_values)
    import greengrassTools.commands.component.build as build
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mock_clean = mocker.patch("greengrassTools.common.utils.clean_dir")
    build.create_gg_build_directories()

    assert mock_mkdir.call_count == 2
    assert mock_clean.call_count == 1

    mock_mkdir.assert_any_call(json_values["gg_build_recipes_dir"],parents=True,exist_ok=True)
    mock_mkdir.assert_any_call(json_values["gg_build_component_artifacts_dir"],parents=True,exist_ok=True)
    mock_clean.assert_called_once_with(json_values["gg_build_directory"])

def test_run_build_command_with_error_not_zip(mocker):
    mock_build_system_zip = mocker.patch("greengrassTools.commands.component.build._build_system_zip", return_value=None)
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None, side_effect=Error('some error'))
    import greengrassTools.commands.component.build as build
    build.project_config["component_build_config"]["build_system"]="maven"
    with pytest.raises(Exception) as e:
        build.run_build_command()
    assert not mock_build_system_zip.called
    assert mock_subprocess_run.called
    assert "Error building the component with the given build system." in e.value.args[0]

def test_run_build_command_with_error_with_zip_build(mocker):
    mock_build_system_zip = mocker.patch("greengrassTools.commands.component.build._build_system_zip", return_value=None, side_effect=Error('some error'))
    import greengrassTools.commands.component.build as build
    build.project_config["component_build_config"]["build_system"]="zip"
    with pytest.raises(Exception) as e:
        build.run_build_command()
    assert "Error building the component with the given build system." in e.value.args[0]
    assert mock_build_system_zip.called

def test_run_build_command_not_zip_build(mocker):
    mock_build_system_zip = mocker.patch("greengrassTools.commands.component.build._build_system_zip", return_value=None)
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    import greengrassTools.commands.component.build as build
    build.project_config["component_build_config"]["build_system"]="maven"
    build.run_build_command()
    assert not mock_build_system_zip.called
    assert mock_subprocess_run.called

def test_run_build_command_zip_build(mocker):
    mock_build_system_zip = mocker.patch("greengrassTools.commands.component.build._build_system_zip", return_value=None)
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    import greengrassTools.commands.component.build as build
    build.project_config["component_build_config"]["build_system"]="zip"
    build.run_build_command()
    assert not mock_subprocess_run.called
    mock_build_system_zip.assert_called_with()

def test_build_system_zip_valid(mocker):
    # build_file = Path('mock-file.py').resolve()
    build_info = {"build_system":"zip", "build_command":[""]}
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path)
    mock_clean_dir = mocker.patch("greengrassTools.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    mock_ignore_files_during_zip = mocker.patch("greengrassTools.commands.component.build._ignore_files_during_zip", return_value = [])
    mock_make_archive = mocker.patch("shutil.make_archive") 
    import greengrassTools.commands.component.build as build
    build.project_config["component_build_config"]["build_system"]="zip"
    build._build_system_zip()

    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    mock_clean_dir.assert_called_with(zip_build_path)

    curr_dir = Path('.').resolve()
    
    mock_copytree.assert_called_with(curr_dir, zip_build_path, dirs_exist_ok=True, ignore=mock_ignore_files_during_zip)
    assert mock_make_archive.called
    zip_build_file = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
    mock_make_archive.assert_called_with(zip_build_file,'zip',root_dir=zip_build_path)

def test_ignore_files_during_zip():
    import greengrassTools.commands.component.build as build
    path = Path('.')
    names = ['1', '2']
    li = build._ignore_files_during_zip(path,names)
    assert type(li) == list

def test_build_system_zip_error_archive(mocker):

    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path)
    mock_clean_dir = mocker.patch("greengrassTools.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    mock_ignore_files_during_zip = mocker.patch("greengrassTools.commands.component.build._ignore_files_during_zip", return_value = [])
    mock_make_archive = mocker.patch("shutil.make_archive", side_effect=Error('some error')) 
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0] 
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    mock_clean_dir.assert_called_with(zip_build_path)

    curr_dir = Path('.').resolve()
    
    mock_copytree.assert_called_with(curr_dir, zip_build_path, dirs_exist_ok=True, ignore=mock_ignore_files_during_zip)
    assert mock_make_archive.called
    zip_build_file = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
    mock_make_archive.assert_called_with(zip_build_file,'zip',root_dir=zip_build_path)


def test_build_system_zip_error_copytree(mocker):
    # build_file = Path('mock-file.py').resolve()
    # build_info = {"build_system":"zip", "build_command":[""]}
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path)
    mock_clean_dir = mocker.patch("greengrassTools.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree", side_effect=Error('some error'))
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    mock_ignore_files_during_zip = mocker.patch("greengrassTools.commands.component.build._ignore_files_during_zip", return_value = [])
    mock_make_archive = mocker.patch("shutil.make_archive") 
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0] 
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    mock_clean_dir.assert_called_with(zip_build_path)

    curr_dir = Path('.').resolve()
    
    mock_copytree.assert_called_with(curr_dir, zip_build_path, dirs_exist_ok=True, ignore=mock_ignore_files_during_zip)
    assert not mock_make_archive.called

    
def test_build_system_zip_error_get_build_folder_by_build_system(mocker):
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path, side_effect=Error('some error'))
    mock_clean_dir = mocker.patch("greengrassTools.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    mock_ignore_files_during_zip = mocker.patch("greengrassTools.commands.component.build._ignore_files_during_zip", return_value = [])
    mock_make_archive = mocker.patch("shutil.make_archive") 
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0] 
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    assert not mock_clean_dir.called
    assert not mock_copytree.called
    assert not mock_make_archive.called

def test_build_system_zip_error_clean_dir(mocker):
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_clean_dir = mocker.patch("greengrassTools.common.utils.clean_dir", return_value=None, side_effect=Error('some error'))
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value = None)
    mock_make_archive = mocker.patch("shutil.make_archive") 
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0] 
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    assert mock_clean_dir.called
    assert not mock_copytree.called
    assert not mock_make_archive.called

def test_copy_artifacts_and_update_uris_valid(mocker):
    mock_get_parsed_config= mocker.patch("greengrassTools.commands.component.project_utils.get_project_config_values", return_value=json_values)
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_shutil_copy = mocker.patch('shutil.copy')
    mock_glob = mocker.patch('pathlib.Path.glob', return_value=[Path('.').joinpath('hello_world.py')])
    import greengrassTools.commands.component.build as build
    build.copy_artifacts_and_update_uris()
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once
    assert mock_shutil_copy.called

def test_copy_artifacts_and_update_uris_recipe_uri_matches(mocker):
    # Copy only if the uri in recipe matches the artifact in build folder
    mock_get_parsed_config= mocker.patch("greengrassTools.commands.component.project_utils.get_project_config_values", return_value=json_values)
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_iter_dir_list=[Path('hello_world.py').resolve()]
    mock_shutil_copy = mocker.patch('shutil.copy')
    mock_glob = mocker.patch('pathlib.Path.glob', return_value=mock_iter_dir_list)
    import greengrassTools.commands.component.build as build
    build.copy_artifacts_and_update_uris()
    assert mock_shutil_copy.called
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once
    mock_shutil_copy.assert_called_with(Path('hello_world.py').resolve(), json_values["gg_build_component_artifacts_dir"])

def test_copy_artifacts_and_update_uris_recipe_uri_not_matches(mocker):
    # Do not copy if the uri in recipe doesnt match the artifact in build folder
    mock_get_parsed_config= mocker.patch("greengrassTools.commands.component.project_utils.get_project_config_values", return_value=json_values)
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_shutil_copy = mocker.patch('shutil.copy')
    mock_glob = mocker.patch('pathlib.Path.glob', return_value=[])
    import greengrassTools.commands.component.build as build
    build_info = {"build_system":"zip", "build_command":[""]}
    with pytest.raises(Exception) as e:
        build.copy_artifacts_and_update_uris()

    assert "Could not find the artifact file specified in the recipe 'hello_world.py' inside the build folder" in e.value.args[0] 
    assert not mock_shutil_copy.called
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once

def test_default_build_component(mocker):
    mock_run_build_command = mocker.patch("greengrassTools.commands.component.build.run_build_command")
    mock_copy_artifacts_and_update_uris = mocker.patch("greengrassTools.commands.component.build.copy_artifacts_and_update_uris")
    mock_create_build_recipe_file = mocker.patch("greengrassTools.commands.component.build.create_build_recipe_file")
    import greengrassTools.commands.component.build as build
    build.default_build_component()
    assert mock_run_build_command.assert_called_once
    assert mock_copy_artifacts_and_update_uris.assert_called_once
    assert mock_create_build_recipe_file.assert_called_once

def test_default_build_component_error_run_build_command(mocker):
    mock_run_build_command = mocker.patch("greengrassTools.commands.component.build.run_build_command",side_effect=Error('command'))
    mock_copy_artifacts_and_update_uris = mocker.patch("greengrassTools.commands.component.build.copy_artifacts_and_update_uris")
    mock_create_build_recipe_file = mocker.patch("greengrassTools.commands.component.build.create_build_recipe_file")
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build.default_build_component()

    assert "\ncommand" in e.value.args[0] 
    assert error_messages.BUILD_FAILED in e.value.args[0]
    assert mock_run_build_command.assert_called_once
    assert not mock_copy_artifacts_and_update_uris.called
    assert not mock_create_build_recipe_file.called

def test_default_build_component_error_copy_artifacts_and_update_uris(mocker):
    mock_run_build_command = mocker.patch("greengrassTools.commands.component.build.run_build_command")
    mock_copy_artifacts_and_update_uris = mocker.patch("greengrassTools.commands.component.build.copy_artifacts_and_update_uris",side_effect=Error('copying'))
    mock_create_build_recipe_file = mocker.patch("greengrassTools.commands.component.build.create_build_recipe_file")
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build.default_build_component()

    assert "\ncopy" in e.value.args[0] 
    assert error_messages.BUILD_FAILED in e.value.args[0]
    assert mock_run_build_command.assert_called_once
    assert mock_copy_artifacts_and_update_uris.assert_called_once
    assert not mock_create_build_recipe_file.called

def test_default_build_component_error_create_build_recipe_file(mocker):
    mock_run_build_command = mocker.patch("greengrassTools.commands.component.build.run_build_command")
    mock_copy_artifacts_and_update_uris = mocker.patch("greengrassTools.commands.component.build.copy_artifacts_and_update_uris")
    mock_create_build_recipe_file = mocker.patch("greengrassTools.commands.component.build.create_build_recipe_file",side_effect=Error('recipe'))
    import greengrassTools.commands.component.build as build
    with pytest.raises(Exception) as e:
        build.default_build_component()

    assert "\nrecipe" in e.value.args[0] 
    assert error_messages.BUILD_FAILED in e.value.args[0] 
    assert mock_run_build_command.assert_called_once
    assert mock_copy_artifacts_and_update_uris.assert_called_once
    assert mock_create_build_recipe_file.assert_called_once

def test_build_run_default(mocker):
    mock_create_gg_build_directories = mocker.patch("greengrassTools.commands.component.build.create_gg_build_directories")
    mock_default_build_component = mocker.patch("greengrassTools.commands.component.build.default_build_component")
    mock_subprocess_run = mocker.patch("subprocess.run")
    import greengrassTools.commands.component.build as build
    build.run({})

    assert mock_create_gg_build_directories.assert_called_once
    assert mock_default_build_component.assert_called_once
    assert not mock_subprocess_run.called

def test_build_run_custom(mocker):
    mock_create_gg_build_directories = mocker.patch("greengrassTools.commands.component.build.create_gg_build_directories")
    mock_default_build_component = mocker.patch("greengrassTools.commands.component.build.default_build_component")
    mock_subprocess_run = mocker.patch("subprocess.run")
    import greengrassTools.commands.component.build as build
    
    modify_build = build.project_config
    modify_build["component_build_config"]["build_system"] ="custom"
    modify_build["component_build_config"]["custom_build_command"] =["a"]
    build.run({})
    assert mock_create_gg_build_directories.assert_called_once
    assert not mock_default_build_component.called
    assert mock_subprocess_run.called

def test_copy_artifacts_and_update_uris_no_manifest_in_recipe(mocker):
    # Nothing to copy if manifest file doesnt exist
    # recipe with no manifest key
    
    import greengrassTools.commands.component.build as build
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_iter_dir_list=[Path('this-recipe-uri-not-exists.sh').resolve()]
    mock_shutil_copy = mocker.patch('shutil.copy')
    mock_glob = mocker.patch('pathlib.Path.iterdir', return_value=mock_iter_dir_list)
    
    build_info = {"build_system":"zip", "build_command":[""]}
    modify_build = build.project_config
    modify_build["parsed_component_recipe"]= {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {
            "DefaultConfiguration": {
                "Message": "world"
            }
        },
        
    }
    build.copy_artifacts_and_update_uris()
    assert not mock_shutil_copy.called
    assert not mock_build_info.called
    assert not mock_glob.called


def test_copy_artifacts_and_update_uris_no_artifacts_in_recipe(mocker):
    # Nothing to copy if artifacts uri in recipe manifest doesnt exist
    
    import greengrassTools.commands.component.build as build
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_iter_dir_list=Path('this-recipe-uri-not-exists.sh').resolve()
    mock_shutil_copy = mocker.patch('shutil.copy')
    mock_glob = mocker.patch('pathlib.Path.glob', return_value=mock_iter_dir_list)
    
    build_info = {"build_system":"zip", "build_command":[""]}
    modify_build = build.project_config
    modify_build["parsed_component_recipe"]= {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {
            "DefaultConfiguration": {
                "Message": "world"
            }
        },
        "Manifests": [
            {
                "Platform": {
                    "os": "linux"
                },
                "Lifecycle": {
                    "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                }
            }
        ]
    }

    build.copy_artifacts_and_update_uris()
    assert not mock_shutil_copy.called
    assert mock_build_info.called
    assert not mock_glob.called

def test_copy_artifacts_and_update_uris_no_artifact_uri_in_recipe(mocker):
    # Nothing to copy if manifest file doesnt exist
    # recipe with no manifest key
    
    import greengrassTools.commands.component.build as build
    zip_build_path= Path('zip-build').resolve()
    mock_build_info = mocker.patch("greengrassTools.commands.component.build._get_build_folder_by_build_system", 
    return_value=zip_build_path)
    mock_iter_dir_list=Path('this-recipe-uri-not-exists.sh').resolve()
    mock_shutil_copy = mocker.patch('shutil.copy')
    mock_glob = mocker.patch('pathlib.Path.glob', return_value=mock_iter_dir_list)
    
    build_info = {"build_system":"zip", "build_command":[""]}
    modify_build = build.project_config
    modify_build["parsed_component_recipe"]= {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {
            "DefaultConfiguration": {
                "Message": "world"
            }
        },
        "Manifests": [
            {
                "Platform": {
                    "os": "linux"
                },
                "Lifecycle": {
                    "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                },
                "Artifacts": [
                    {
                        
                    }
                ]
            }
        ]
    }

    build.copy_artifacts_and_update_uris()
    assert not mock_shutil_copy.called
    assert mock_build_info.called
    assert not mock_glob.called