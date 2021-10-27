import greengrassTools.commands.component.init as init
import pytest
import greengrassTools.common.exceptions.error_messages as error_messages
from pathlib import Path
from unittest.mock import patch,mock_open
from urllib3.exceptions import HTTPError

def test_init_run_with_non_empty_directory(mocker):
    ## Test that an exception is raised when init is run in non-empty directory
    test_d_args={'language': 'python', 'template': 'name'}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=False)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)
    mock_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.conflicting_arg_groups",
        return_value=False)
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0]== error_messages.INIT_NON_EMPTY_DIR_ERROR

    assert mock_is_directory_empty.call_count == 1
    assert mock_conflicting_args.call_count == 0
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    
def test_init_run_with_empty_directory(mocker):
    ## Test that an exception is not raised when init is run in an empty directory
    test_d_args={'repository': 'repository'}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=True)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)
    mock_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.conflicting_arg_groups",
        return_value=False)
    init.run(test_d_args)

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 1
    assert mock_conflicting_args.call_count == 1

def test_init_run_with_empty_args_repository(mocker):
    ## Test that an exception is not raised when init is run in an empty directory
    test_d_args={'repository': None}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=True)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)
    mock_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.conflicting_arg_groups",
        return_value=False)
    
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0]== error_messages.INIT_WITH_INVALID_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    assert mock_conflicting_args.call_count == 1

def test_init_run_with_empty_args_template(mocker):
    ## Test that an exception is not raised when init is run in an empty directory
    test_d_args={'template': None, 'language':'python'}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=True)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)
    mock_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.conflicting_arg_groups",
        return_value=False)
    
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0]== error_messages.INIT_WITH_INVALID_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    assert mock_conflicting_args.call_count == 1

def test_init_run_with_conflicting_args(mocker):
    ## Test that an exception is not raised when init is run in an empty directory
    test_d_args={'repository': 'repository'}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=True)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)
    mock_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.conflicting_arg_groups",
        return_value=True)
    
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0]== error_messages.INIT_WITH_CONFLICTING_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    assert mock_conflicting_args.call_count == 1

def test_init_run_with_valid_args(mocker):
    ## Checks if args are used correctly to run correct init method
    test_d_args={'language': 'python', 'template': 'name'}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=True)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)

    init.run(test_d_args)

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 1
    assert mock_init_with_repository.call_count == 0

def test_init_run_with_invalid_args(mocker):
    test_d_args={'lang': 'python', 'template': 'name'}
    mock_is_directory_empty = mocker.patch(
        "greengrassTools.common.utils.is_directory_empty",
        return_value=True)
    mock_init_with_template = mocker.patch(
        "greengrassTools.commands.component.init.init_with_template",
        return_value=None)
    mock_init_with_repository = mocker.patch(
        "greengrassTools.commands.component.init.init_with_repository",
        return_value=None)
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0]== error_messages.INIT_WITH_INVALID_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0

def test_init_with_template_valid(mocker):
    template = "template"
    language = "language"
    template_name_zip = "template-language.zip"
    mock_get_available_templates=mocker.patch("greengrassTools.commands.component.init.get_available_templates_from_github",
    return_value={"template-language":"template-url"})

    mock_response = mocker.Mock(status_code=200)
    mock_template_download=mocker.patch("requests.get",return_value=mock_response)

    mock_unzip_template_zip=mocker.patch("shutil.unpack_archive",return_value=None)
    mock_remove_template_zip=mocker.patch("os.remove", return_value=None)  
    file_path = "path/to/open" 
    with patch("builtins.open", mock_open()) as mock_file:
        init.init_with_template(template,language)
        assert mock_remove_template_zip.call_count == 1
        assert mock_unzip_template_zip.call_count == 1
        assert mock_template_download.call_count == 1
        assert mock_get_available_templates.call_count == 1
        mock_file.assert_called_once_with(template_name_zip, 'wb')

        mock_remove_template_zip.assert_called_with(template_name_zip)
        mock_unzip_template_zip.assert_called_with(template_name_zip, Path('.').resolve())

def test_init_with_template_invalid_url(mocker):
    # Raises an exception when the template url is not valid. 
    template = "template"
    language = "language"
    mock_get_available_templates=mocker.patch("greengrassTools.commands.component.init.get_available_templates_from_github",
    return_value={"template-language":"template-url"})
    mock_response = mocker.Mock(status_code=404, raise_for_status = mocker.Mock(side_effect=HTTPError('some error')))
    mock_template_download=mocker.patch("requests.get",return_value=mock_response)

    mock_unzip_template_zip=mocker.patch("shutil.unpack_archive",
    return_value=None)
    mock_remove_template_zip=mocker.patch("os.remove",
    return_value=None)  
    
    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            init.init_with_template(template,language)

        assert e.value.args[0]== error_messages.INIT_FAILS_DURING_TEMPLATE_DOWNLOAD
        assert mock_remove_template_zip.call_count == 0
        assert mock_unzip_template_zip.call_count == 0
        assert mock_template_download.call_count == 1
        assert mock_get_available_templates.call_count == 1
        assert not mock_file.called

def test_init_with_template_not_available(mocker):
    # Check if an exception is raised when the template is not available
    template = "template"
    language = "language"

    mock_get_available_templates=mocker.patch("greengrassTools.commands.component.init.get_available_templates_from_github",
    return_value=[])
    mock_template_download=mocker.patch("requests.get",
    return_value=None)
    mock_unzip_template_zip=mocker.patch("shutil.unpack_archive",
    return_value=None)
    mock_remove_template_zip=mocker.patch("os.remove",
    return_value=None)   

    with pytest.raises(Exception) as e:
        init.init_with_template(template,language)

    assert e.value.args[0]== error_messages.INIT_WITH_INVALID_TEMPLATE

    assert mock_remove_template_zip.call_count == 0
    assert mock_unzip_template_zip.call_count == 0
    assert mock_template_download.call_count == 0
    assert mock_get_available_templates.call_count == 1
    
    
def test_get_available_templates_from_github_valid_json(mocker):
    res_json ={"template-name":"template-list"}
    mock_response = mocker.Mock(status_code=200, json=lambda: res_json)
    mock_template_list=mocker.patch("requests.get",return_value=mock_response)   

    templates_list = init.get_available_templates_from_github()
    assert templates_list == res_json
    assert mock_template_list.call_count ==1 

def test_get_available_templates_from_github_invalid_json(mocker):
    res_json ={"template-name":"template-list"}
    mock_response = mocker.Mock(status_code=200, json=res_json)
    mock_template_list=mocker.patch("requests.get",return_value=mock_response)   

    templates_list = init.get_available_templates_from_github()
    assert templates_list == []
    assert mock_template_list.call_count ==1

def test_get_available_templates_from_github_invalid_url(mocker):
    res_json ={}
    mock_response = mocker.Mock(status_code=404, raise_for_status = mocker.Mock(side_effect=HTTPError('some error')))
    mock_template_list=mocker.patch("requests.get",return_value=mock_response)  

    with pytest.raises(Exception) as e:
        init.get_available_templates_from_github()
        
    assert e.value.args[0]== error_messages.INIT_FAILS_DURING_LISTING_TEMPLATES
    assert mock_template_list.call_count ==1 
    