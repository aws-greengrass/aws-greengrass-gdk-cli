import pytest
from gdk.wizard.commons.checkers import WizardChecker
from gdk.wizard.commands.data import WizardData
from gdk.wizard.commons.fields import Fields
from pathlib import Path


@pytest.mark.parametrize(
    "valid_author",
    ["test", "''[]''"],
)
def test_check_author_valid(mocker, valid_author):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(valid_author, Fields.AUTHOR) is True


@pytest.mark.parametrize(
    "invalid_author",
    [""],
)
def test_check_author_invalid(mocker, invalid_author):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(invalid_author, Fields.AUTHOR) is False


@pytest.mark.parametrize(
    "valid_version",
    ["12.32.45", "1.2.3-alpha", "NEXT_PATCH"],
)
def test_check_version_valid(mocker, valid_version):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(valid_version, Fields.VERSION) is True


@pytest.mark.parametrize(
    "invalid_version",
    ["alpha", "jadnjadnjq8e", "...", "12..", "a.b.c", "1.b.3"],
)
def test_check_version_invalid(mocker, invalid_version):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(invalid_version, Fields.VERSION) is False


@pytest.mark.parametrize(
    "valid_build_system",
    ["zip", "maven", "gradle", "gradlew", "custom"],
)
def test_check_build_system_valid(mocker, valid_build_system):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(valid_build_system, Fields.BUILD_SYSTEM) is True


@pytest.mark.parametrize(
    "invalid_build_system",
    ["Zip", "random", "123", "True", "None", "{}", "[]"],
)
def test_check_build_system_invalid(mocker, invalid_build_system):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(invalid_build_system, Fields.BUILD_SYSTEM) is False


@pytest.mark.parametrize(
    "valid_custom_build_command",
    ["['one', 'two', 'three']", "['ok']", "test", "['{'foo', 'bar'}', 'test']"],
)
def test_check_custom_build_commands_valid(mocker, valid_custom_build_command):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert (
        checker.is_valid_input(valid_custom_build_command, Fields.CUSTOM_BUILD_COMMAND)
        is True
    )


@pytest.mark.parametrize(
    "invalid_custom_build_command",
    ["{'foo', 'bar'}", "[1,2,3]", "[]", "", "['string1', 'string2', {'ok': 'test'}]"],
)
def test_check_custom_build_commands_invalid(mocker, invalid_custom_build_command):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert (
        checker.is_valid_input(
            invalid_custom_build_command, Fields.CUSTOM_BUILD_COMMAND
        )
        is False
    )


@pytest.mark.parametrize(
    "valid_build_options",
    [
        '{"excludes": [".gitignore", "temp/"], "zip_name": "my_component.zip"}',
        '{"excludes": [".gitignore"], "zip_name": "my_component.zip"}',
    ],
)
def test_check_build_options_valid(mocker, valid_build_options):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(valid_build_options, Fields.BUILD_OPTIONS) is True


@pytest.mark.parametrize(
    "invalid_build_options",
    ["{'foo', 'bar'}", "[1,2,3]", "[]", "", "['string1', 'string2', {'ok': 'test'}]"],
)
def test_check_build_options_invalid(mocker, invalid_build_options):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    data = WizardData()
    checker = WizardChecker(data)
    assert mock_get_project_config_file.called
    assert checker.is_valid_input(invalid_build_options, Fields.BUILD_OPTIONS) is False
