import pytest
from gdk.wizard.WizardChecker import WizardChecker
from gdk.wizard.ConfigEnum import ConfigEnum


@pytest.mark.parametrize(
    "valid_author",
    ["test", "''[]''"],
)
def test_check_author_valid(valid_author):
    checker = WizardChecker()
    assert checker.is_valid_input(valid_author, ConfigEnum.AUTHOR) is True


@pytest.mark.parametrize(
    "invalid_author",
    [""],
)
def test_check_author_invalid(invalid_author):
    checker = WizardChecker()
    assert checker.is_valid_input(invalid_author, ConfigEnum.AUTHOR) is False


@pytest.mark.parametrize(
    "valid_version",
    ["12.32.45", "1.2.3-alpha", "NEXT_PATCH"],
)
def test_check_version_valid(valid_version):
    checker = WizardChecker()
    assert checker.is_valid_input(valid_version, ConfigEnum.VERSION) is True


@pytest.mark.parametrize(
    "invalid_version",
    ["alpha", "jadnjadnjq8e", "...", "12..", "a.b.c", "1.b.3"],
)
def test_check_version_invalid(invalid_version):
    checker = WizardChecker()
    assert checker.is_valid_input(invalid_version, ConfigEnum.VERSION) is False


@pytest.mark.parametrize(
    "valid_build_system",
    ["zip", "maven", "gradle", "gradlew", "custom"],
)
def test_check_build_system_valid(valid_build_system):
    checker = WizardChecker()
    assert checker.is_valid_input(valid_build_system, ConfigEnum.BUILD_SYSTEM) is True


@pytest.mark.parametrize(
    "invalid_build_system",
    ["Zip", "random", "123", "True", "None", "{}", "[]"],
)
def test_check_build_system_invalid(mocker, invalid_build_system):
    checker = WizardChecker()
    assert (
        checker.is_valid_input(invalid_build_system, ConfigEnum.BUILD_SYSTEM) is False
    )


@pytest.mark.parametrize(
    "valid_custom_build_command",
    ["['one', 'two', 'three']", "['ok']", "test", "['{'foo', 'bar'}', 'test']"],
)
def test_check_custom_build_commands_valid(mocker, valid_custom_build_command):
    checker = WizardChecker()
    assert (
        checker.is_valid_input(
            valid_custom_build_command, ConfigEnum.CUSTOM_BUILD_COMMAND
        )
        is True
    )


@pytest.mark.parametrize(
    "invalid_custom_build_command",
    ["{'foo', 'bar'}", "[1,2,3]", "[]", "", "['string1', 'string2', {'ok': 'test'}]"],
)
def test_check_custom_build_commands_invalid(mocker, invalid_custom_build_command):
    checker = WizardChecker()
    assert (
        checker.is_valid_input(
            invalid_custom_build_command, ConfigEnum.CUSTOM_BUILD_COMMAND
        )
        is False
    )
