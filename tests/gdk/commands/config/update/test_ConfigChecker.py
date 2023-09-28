import pytest

from gdk.commands.config.update.ConfigChecker import ConfigChecker
from gdk.commands.config.update.ConfigEnum import ConfigEnum


@pytest.mark.parametrize(
    "valid_component_name",
    ["test", "com.example.HelloWorldComponent"],
)
def test_check_component_name_valid(valid_component_name):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_component_name, ConfigEnum.COMPONENT_NAME) is True


@pytest.mark.parametrize(
    "invalid_component_name",
    [""],
)
def test_check_component_name_invalid(invalid_component_name):
    checker = ConfigChecker()
    assert checker.is_valid_input(invalid_component_name, ConfigEnum.COMPONENT_NAME) is False


@pytest.mark.parametrize(
    "valid_author",
    ["test", "''[]''"],
)
def test_check_author_valid(valid_author):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_author, ConfigEnum.AUTHOR) is True


@pytest.mark.parametrize(
    "invalid_author",
    [""],
)
def test_check_author_invalid(invalid_author):
    checker = ConfigChecker()
    assert checker.is_valid_input(invalid_author, ConfigEnum.AUTHOR) is False


@pytest.mark.parametrize(
    "valid_version",
    ["12.32.45", "1.2.3-alpha", "NEXT_PATCH"],
)
def test_check_version_valid(valid_version):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_version, ConfigEnum.VERSION) is True


@pytest.mark.parametrize(
    "invalid_version",
    ["alpha", "jadnjadnjq8e", "...", "12..", "a.b.c", "1.b.3"],
)
def test_check_version_invalid(invalid_version):
    checker = ConfigChecker()
    assert checker.is_valid_input(invalid_version, ConfigEnum.VERSION) is False


@pytest.mark.parametrize(
    "valid_build_system",
    ["zip", "maven", "gradle", "gradlew", "custom"],
)
def test_check_build_system_valid(valid_build_system):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_build_system, ConfigEnum.BUILD_SYSTEM) is True


@pytest.mark.parametrize(
    "invalid_build_system",
    ["Zip", "random", "123", "True", "None", "{}", "[]"],
)
def test_check_build_system_invalid(invalid_build_system):
    checker = ConfigChecker()
    assert (
        checker.is_valid_input(invalid_build_system, ConfigEnum.BUILD_SYSTEM) is False
    )


@pytest.mark.parametrize(
    "valid_custom_build_command",
    [
        "['one', 'two', 'three']",
        "['ok']",
        "test",
        "[\"{'foo', 'bar'}\", 'test']",
        "x+y",
    ],
)
def test_check_custom_build_commands_valid(valid_custom_build_command):
    checker = ConfigChecker()
    assert (
        checker.is_valid_input(
            valid_custom_build_command, ConfigEnum.CUSTOM_BUILD_COMMAND
        )
        is True
    )


@pytest.mark.parametrize(
    "invalid_custom_build_command",
    [
        "{'foo', 'bar'}",
        "[1,2,3]",
        "[]",
        "",
        "()",
        "{}",
        "['string1', 'string2', {'ok': 'test'}]",
        "('one', 'two', 'three')",
        "None",
    ],
)
def test_check_custom_build_commands_invalid(invalid_custom_build_command):
    checker = ConfigChecker()
    assert (
        checker.is_valid_input(
            invalid_custom_build_command, ConfigEnum.CUSTOM_BUILD_COMMAND
        )
        is False
    )


@pytest.mark.parametrize(
    "valid_build_options",
    [
        '{"excludes": [".gitignore", "temp/"], "zip_name": "my_component.zip"}',
        '{"excludes": [".gitignore"], "zip_name": "my_component.zip", "extra": "foo"}',
        '{"EXCLUDES": [".gitignore"], "ZIP_NAME": "my_component.zip"}',
        '{"excludes": [], "zip_name": ""}',
        "{}",
    ],
)
def test_check_build_options_valid(valid_build_options):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_build_options, ConfigEnum.BUILD_OPTIONS) is True


@pytest.mark.parametrize(
    "invalid_build_options",
    [
        '{"foo", "bar"}',
        "[1,2,3]",
        "[]",
        "",
        '["string1", "string2", {"ok": "test"}]',
        '("string1", "string2", {"ok": "test"})',
        '{"excludes": [], "zip_name": 7}',
        '{"excludes": {}, "zip_name": ""}',
        '{"excludes": ["ok", 2], "zip_name": ""}',
    ],
)
def test_check_build_options_invalid(invalid_build_options):
    checker = ConfigChecker()
    assert (
        checker.is_valid_input(invalid_build_options, ConfigEnum.BUILD_OPTIONS) is False
    )


@pytest.mark.parametrize(
    "valid_bucket",
    ["random-bucket", "123456789[;...AR]"],
)
def test_check_bucket_valid(valid_bucket):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_bucket, ConfigEnum.BUCKET) is True


@pytest.mark.parametrize(
    "invalid_bucket",
    [""],
)
def test_check_bucket_invalid(invalid_bucket):
    checker = ConfigChecker()
    assert checker.is_valid_input(invalid_bucket, ConfigEnum.BUCKET) is False


@pytest.mark.parametrize(
    "valid_region",
    ["random-region", "123456789[;...AR]"],
)
def test_check_region_valid(valid_region):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_region, ConfigEnum.REGION) is True


@pytest.mark.parametrize(
    "invalid_region",
    [""],
)
def test_check_region_invalid(invalid_region):
    checker = ConfigChecker()
    assert checker.is_valid_input(invalid_region, ConfigEnum.REGION) is False


@pytest.mark.parametrize(
    "valid_publish_options",
    [
        '{"file_upload_args": {"bucket": "bucket1"}}',
        '{"file_upload_args": {}}',
        "{}",
        '{"ok": "bar"}',
    ],
)
def test_check_publish_options_valid(valid_publish_options):
    checker = ConfigChecker()
    assert (
        checker.is_valid_input(valid_publish_options, ConfigEnum.PUBLISH_OPTIONS)
        is True
    )


@pytest.mark.parametrize(
    "invalid_publish_options",
    [
        "",
        '{"file_upload_args": {"options1"}}',
        '{"file_upload_args": "options1"}',
        '{"file_upload_args": }',
        '{"options1"}',
        "[]",
        '("ok", "bar")',
        "ajdajndj",
        "1233jada",
    ],
)
def test_check_publish_options_invalid(invalid_publish_options):
    checker = ConfigChecker()
    assert (
        checker.is_valid_input(invalid_publish_options, ConfigEnum.PUBLISH_OPTIONS)
        is False
    )


@pytest.mark.parametrize(
    "valid_gdk_version",
    ["12.32.45", "1.2.3-alpha"],
)
def test_check_gdk_version_valid(valid_gdk_version):
    checker = ConfigChecker()
    assert checker.is_valid_input(valid_gdk_version, ConfigEnum.GDK_VERSION) is True


@pytest.mark.parametrize(
    "invalid_gdk_version",
    ["alpha", "jadnjadnjq8e", "...", "12..", "a.b.c", "1.b.3"],
)
def test_check_gdk_version_invalid(invalid_gdk_version):
    checker = ConfigChecker()
    assert checker.is_valid_input(invalid_gdk_version, ConfigEnum.GDK_VERSION) is False
