import pytest
from unittest import TestCase
from unittest.mock import call
from gdk.commands.test.BuildCommand import BuildCommand
from pathlib import Path
from unittest import mock
import platform


class BuildCommandUnitTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

        config = {
            "component": {
                "abc": {
                    "author": "abc",
                    "version": "1.0.0",
                    "build": {"build_system": "zip"},
                    "publish": {"bucket": "default", "region": "us-east-1"},
                }
            }
        }

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        self.mocker.patch("gdk.commands.component.project_utils.get_recipe_file", return_value=Path("."))

    def test_update_features_with_no_interpolation(self):
        build_cmd = BuildCommand({})
        mock_rglob = self.mocker.patch("pathlib.Path.rglob", return_value=[Path("abc.feature")])

        with mock.patch("builtins.open", mock.mock_open(read_data="nothing_to_update")) as mock_file:
            build_cmd.update_feature_files("recipe.yaml", "uat_recipe.yaml")
            assert mock_file.call_args_list == [call(Path(".").joinpath("abc.feature"), "r", encoding="utf-8")]

        assert mock_rglob.call_args_list == [call("*.feature")]

    def test_update_features_with_component_name_interpolation(self):
        self.mocker.patch("pathlib.Path.as_uri", return_value="file:///abc.feature")
        mock_rglob = self.mocker.patch("pathlib.Path.rglob", return_value=[Path("abc.feature")])
        build_cmd = BuildCommand({})

        with mock.patch("builtins.open", mock.mock_open(read_data="This is GDK_COMPONENT_NAME")) as mock_file:
            build_cmd.update_feature_files("recipe.yaml", "uat_recipe.yaml")
            assert mock_file.call_args_list == [
                call(Path(".").joinpath("abc.feature"), "r", encoding="utf-8"),
                call(Path(".").joinpath("abc.feature"), "w", encoding="utf-8"),
            ]

            assert mock_file.return_value.write.call_args_list == [call("This is abc")]

        assert mock_rglob.call_args_list == [call("*.feature")]

    def test_update_features_with_component_recipe_file_interpolation(self):
        mock_rglob = self.mocker.patch("pathlib.Path.rglob", return_value=[Path("abc.feature")])
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        self.mocker.patch("pathlib.Path.as_uri", return_value="file:///abc.feature")
        build_cmd = BuildCommand({})

        with mock.patch(
            "builtins.open", mock.mock_open(read_data="This is GDK_COMPONENT_NAME and GDK_COMPONENT_RECIPE_FILE")
        ) as mock_file:
            build_cmd.update_feature_files(Path("recipe.yaml"), Path("uat_recipe.yaml"))
            assert mock_file.call_args_list == [
                call(Path(".").joinpath("abc.feature"), "r", encoding="utf-8"),
                call(Path(".").joinpath("abc.feature"), "w", encoding="utf-8"),
            ]
            assert mock_file.return_value.write.call_args_list == [call("This is abc and file:///abc.feature")]

        assert mock_rglob.call_args_list == [call("*.feature")]

    def test_update_features_with_component_recipe_file_without_build_raises_exception(self):
        mock_rglob = self.mocker.patch("pathlib.Path.rglob", return_value=[Path("abc.feature")])
        self.mocker.patch("pathlib.Path.exists", return_value=False)
        self.mocker.patch("pathlib.Path.as_uri", return_value="file:///abc.feature")
        build_cmd = BuildCommand({})

        with mock.patch(
            "builtins.open", mock.mock_open(read_data="This is GDK_COMPONENT_NAME and GDK_COMPONENT_RECIPE_FILE")
        ) as mock_file:
            with pytest.raises(Exception) as e:
                build_cmd.update_feature_files(Path("recipe.yaml"), Path("uat_recipe.yaml"))
                assert mock_file.call_args_list == [call(Path(".").joinpath("abc.feature"), "r", encoding="utf-8")]
            assert "Component is not built" in e.value.args[0]

        assert mock_rglob.call_args_list == [call("*.feature")]

    def test_create_uat_recipe_from_build_recipe_without_replacing_s3_uri(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        self.mocker.patch("pathlib.Path.as_uri", return_value="file:///abc.feature")
        build_cmd = BuildCommand({})
        build_cmd.should_create_uat_recipe = True
        with mock.patch("builtins.open", mock.mock_open(read_data="recipe with s3://BUCKET/abc.feature")) as mock_file:
            build_cmd.create_uat_recipe_file(Path("recipe.yaml"), Path("uat_recipe.yaml"))
            assert mock_file.call_args_list == [
                call(Path(".").joinpath("recipe.yaml"), "r", encoding="utf-8"),
                call(Path(".").joinpath("uat_recipe.yaml"), "w", encoding="utf-8"),
            ]
            assert mock_file.return_value.write.call_args_list == [call("recipe with s3://BUCKET/abc.feature")]

    def test_create_uat_recipe_from_build_recipe_with_replacing_s3_uri(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)

        def get_as_uris(self):
            return str(self)

        self.mocker.patch.object(Path, "as_uri", get_as_uris)
        build_cmd = BuildCommand({})
        build_cmd.should_create_uat_recipe = True
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="recipe with s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/somefile.json"),
        ) as mock_file:
            build_cmd.create_uat_recipe_file(Path("recipe.yaml"), Path("uat_recipe.yaml"))
            assert mock_file.call_args_list == [
                call(Path(".").joinpath("recipe.yaml"), "r", encoding="utf-8"),
                call(Path(".").joinpath("uat_recipe.yaml"), "w", encoding="utf-8"),
            ]

            print(mock_file.return_value.write.call_args_list)
            assert mock_file.return_value.write.call_args_list == [
                call(
                    "recipe with "
                    + Path().absolute().joinpath("greengrass-build/artifacts/abc/1.0.0/somefile.json").resolve().as_uri()
                )
            ]

    def test_create_uat_recipe_from_should_not_create_uat_recipe(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)

        def get_as_uris(self):
            return str(self)

        self.mocker.patch.object(Path, "as_uri", get_as_uris)
        build_cmd = BuildCommand({})
        build_cmd.should_create_uat_recipe = False
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="recipe with s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/somefile.json"),
        ) as mock_file:
            build_cmd.create_uat_recipe_file(Path("recipe.yaml"), Path("uat_recipe.yaml"))
            assert mock_file.call_args_list == []

    def test_build_uat_module(self):
        uat_build_cmd = self.mocker.patch("subprocess.run", return_value=None)
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        build_cmd = BuildCommand({})
        build_cmd.build_uat_module()

        if platform.system() == "Windows":
            assert uat_build_cmd.call_args_list == [
                call(
                    ["mvn.cmd", "package"],
                    check=True,
                    cwd=Path().absolute().joinpath("greengrass-build/uat-features").resolve(),
                )
            ]
        else:
            assert uat_build_cmd.call_args_list == [
                call(["mvn", "package"], check=True, cwd=Path().absolute().joinpath("greengrass-build/uat-features").resolve())
            ]