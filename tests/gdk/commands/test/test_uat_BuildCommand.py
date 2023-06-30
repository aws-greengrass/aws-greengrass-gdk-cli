import pytest
from unittest import TestCase
from unittest.mock import call, ANY
from gdk.commands.test.BuildCommand import BuildCommand
from pathlib import Path
from unittest import mock
import platform
from gdk.common.CaseInsensitive import CaseInsensitiveDict, CaseInsensitiveRecipeFile
import os
import gdk.common.consts as consts
from gdk.common.config.GDKProject import GDKProject


class BuildCommandUnitTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()

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
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_update_features_with_no_interpolation(self):
        build_cmd = BuildCommand({})
        mock_rglob = self.mocker.patch("pathlib.Path.rglob", return_value=[Path("abc.feature")])

        with mock.patch("builtins.open", mock.mock_open(read_data="nothing_to_update")) as mock_file:
            build_cmd.update_feature_files("recipe.yaml", "e2e_test_recipe.yaml")
            assert mock_file.call_args_list == [call(Path(".").joinpath("abc.feature"), "r", encoding="utf-8")]

        assert mock_rglob.call_args_list == [call("*.feature")]

    def test_update_features_with_component_name_interpolation(self):
        self.mocker.patch("pathlib.Path.as_uri", return_value="file:///abc.feature")
        mock_rglob = self.mocker.patch("pathlib.Path.rglob", return_value=[Path("abc.feature")])
        build_cmd = BuildCommand({})

        with mock.patch("builtins.open", mock.mock_open(read_data="This is GDK_COMPONENT_NAME")) as mock_file:
            build_cmd.update_feature_files("recipe.yaml", "e2e_test_recipe.yaml")
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
            build_cmd.update_feature_files(Path("recipe.yaml"), Path("e2e_test_recipe.yaml"))
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
                build_cmd.update_feature_files(Path("recipe.yaml"), Path("e2e_test_recipe.yaml"))
                assert mock_file.call_args_list == [call(Path(".").joinpath("abc.feature"), "r", encoding="utf-8")]
            assert "Component is not built" in e.value.args[0]

        assert mock_rglob.call_args_list == [call("*.feature")]

    def test_GIVEN_build_recipe_witj_NEXT_PATCH_and_no_s3_uris_WHEN_create_test_reicpe_THEN_update_version_only(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        self.mocker.patch("pathlib.Path.as_uri", return_value="file:///abc.feature")
        build_cmd = BuildCommand({})
        build_cmd.should_create_e2e_test_recipe = True
        test_recipe = {"componentVersion": "NEXT_PATCH", "manifests": [{"artifacts": [{"Uri": "docker://somefile.json"}]}]}
        mock_read = self.mocker.patch(
            "gdk.common.CaseInsensitive.CaseInsensitiveRecipeFile.read",
            return_value=CaseInsensitiveDict(test_recipe),
        )
        spy_write = self.mocker.spy(CaseInsensitiveRecipeFile, "write")
        updated_recipe = {"componentVersion": "1.0.0", "manifests": [{"artifacts": [{"Uri": "docker://somefile.json"}]}]}

        build_cmd.create_e2e_test_recipe_file(Path("recipe.yaml"), Path("e2e_test_recipe.yaml"))
        assert mock_read.call_args_list == [call(Path(".").joinpath("recipe.yaml"))]
        assert spy_write.call_args_list == [call(ANY, Path("e2e_test_recipe.yaml"), updated_recipe)]

    def test_create_e2e_test_recipe_from_build_recipe_with_replacing_version_and_uris(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)

        def get_as_uris(self):
            return str(self)

        self.mocker.patch.object(Path, "as_uri", get_as_uris)
        build_cmd = BuildCommand({})
        build_cmd.should_create_e2e_test_recipe = True
        test_recipe = {"componentVersion": "2.2.2", "manifests": [{"artifacts": [{"Uri": "s3://somefile.json"}]}]}
        updated_recipe = {
            "componentVersion": "2.2.2",
            "manifests": [
                {
                    "artifacts": [
                        {
                            "Uri": Path()
                            .absolute()
                            .joinpath("greengrass-build/artifacts/abc/1.0.0/somefile.json")
                            .resolve()
                            .as_uri()
                        }
                    ]
                }
            ],
        }
        mock_read = self.mocker.patch(
            "gdk.common.CaseInsensitive.CaseInsensitiveRecipeFile.read",
            return_value=CaseInsensitiveDict(test_recipe),
        )

        spy_write = self.mocker.spy(CaseInsensitiveRecipeFile, "write")
        build_cmd.create_e2e_test_recipe_file(Path("recipe.yaml"), Path("e2e_test_recipe.yaml"))
        assert mock_read.call_args_list == [call(Path(".").joinpath("recipe.yaml"))]
        assert spy_write.call_args_list == [call(ANY, Path("e2e_test_recipe.yaml"), updated_recipe)]

    def test_create_e2e_test_recipe_from_should_not_create_e2e_test_recipe(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)

        def get_as_uris(self):
            return str(self)

        self.mocker.patch.object(Path, "as_uri", get_as_uris)
        build_cmd = BuildCommand({})
        build_cmd.should_create_e2e_test_recipe = False
        test_recipe = {"manifests": [{"artifacts": [{"Uri": "s3://somefile.json"}]}]}
        mock_read = self.mocker.patch(
            "gdk.common.CaseInsensitive.CaseInsensitiveRecipeFile.read",
            return_value=CaseInsensitiveDict(test_recipe),
        )
        build_cmd.create_e2e_test_recipe_file(Path("recipe.yaml"), Path("e2e_test_recipe.yaml"))
        assert not mock_read.call_args_list == [call(Path(".").joinpath("recipe.yaml"))]

    def test_GIVEN_build_recipe_with_s3_URIs_and_version_WHEN_create_test_recipe_THEN_no_update_in_recipe(self):
        self.mocker.patch("pathlib.Path.exists", return_value=False)

        def get_as_uris(self):
            return str(self)

        self.mocker.patch.object(Path, "as_uri", get_as_uris)
        build_cmd = BuildCommand({})
        build_cmd.should_create_e2e_test_recipe = True
        test_recipe = {"componentVersion": "1.0.0", "manifests": [{"artifacts": [{"Uri": "s3://somefile.json"}]}]}
        mock_read = self.mocker.patch(
            "gdk.common.CaseInsensitive.CaseInsensitiveRecipeFile.read",
            return_value=CaseInsensitiveDict(test_recipe),
        )
        spy_write = self.mocker.spy(CaseInsensitiveRecipeFile, "write")
        build_cmd.create_e2e_test_recipe_file(Path("recipe.yaml"), Path("e2e_test_recipe.yaml"))
        assert mock_read.call_args_list == [call(Path(".").joinpath("recipe.yaml"))]
        assert spy_write.call_args_list == [call(ANY, Path("e2e_test_recipe.yaml"), test_recipe)]

    def test_build_e2e_test_module(self):
        e2e_test_build_cmd = self.mocker.patch("subprocess.run", return_value=None)
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        build_cmd = BuildCommand({})
        build_cmd.build_e2e_test_module()

        if platform.system() == "Windows":
            assert e2e_test_build_cmd.call_args_list == [
                call(
                    ["mvn.cmd", "package"],
                    check=True,
                    cwd=Path().absolute().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}").resolve(),
                )
            ]
        else:
            assert e2e_test_build_cmd.call_args_list == [
                call(
                    ["mvn", "package"],
                    check=True,
                    cwd=Path().absolute().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}").resolve(),
                )
            ]
