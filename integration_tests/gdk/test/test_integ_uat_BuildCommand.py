from unittest import TestCase

import pytest
from pathlib import Path
import os
from gdk.commands.test.BuildCommand import BuildCommand
from gdk.build_system.Maven import Maven
import shutil


class UATBuildCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        self.mocker.patch("gdk.commands.component.project_utils.get_recipe_file", return_value=Path("recipe.yaml"))
        self.mocker.patch.object(Maven, "build", return_value=None)
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_when_test_module_build_then_update_features(self):
        self.setup_test_data_config("config.json")
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml").resolve(),
            Path(self.tmpdir).joinpath("greengrass-build/recipes").joinpath("recipe.yaml").resolve(),
        )

        artifact_path = Path(self.tmpdir).joinpath("greengrass-build/artifacts/abc/NEXT_PATCH").joinpath("hello_world.py")
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.touch()

        # Test
        build_command = BuildCommand({})
        build_command.run()

        uat_recipe_file = Path(self.tmpdir).joinpath("greengrass-build/recipes").joinpath("uat_recipe.yaml")
        uat_features = Path(self.tmpdir).joinpath("greengrass-build/uat-features")

        assert uat_recipe_file.exists()
        assert uat_features.exists()
        with open(uat_recipe_file, mode="r") as f:
            content = f.read()
            assert Path(self.tmpdir).joinpath("greengrass-build/artifacts/abc/NEXT_PATCH").as_uri() in content
        with open(uat_features.joinpath("src/main/resources/greengrass/features/component.feature"), mode="r") as f:
            content = f.read()
            assert uat_recipe_file.as_uri() in content

        with open(
            Path(self.tmpdir).joinpath("uat-features/src/main/resources/greengrass/features/component.feature"), mode="r"
        ) as f:
            content = f.read()
            assert uat_recipe_file.as_uri() not in content

    def test_when_test_module_build_with_no_interpolation_then_do_not_create_uat_recipe_file(self):
        # Setup test data. Update the feature files ahead so the build command has nothing to update.
        self.setup_test_data_config("config.json")
        uat_features = Path(self.tmpdir).joinpath("uat-features")
        with open(uat_features.joinpath("src/main/resources/greengrass/features/component.feature"), mode="r") as f:
            content = f.read()
            content = content.replace("GDK_COMPONENT_NAME", "some-component-name").replace(
                "GDK_COMPONENT_RECIPE_FILE", "some-recipe-file"
            )

        with open(uat_features.joinpath("src/main/resources/greengrass/features/component.feature"), mode="w") as f:
            f.write(content)

        # Test
        build_command = BuildCommand({})
        build_command.run()
        uat_recipe_file = Path(self.tmpdir).joinpath("greengrass-build/recipes").joinpath("uat_recipe.yaml")

        assert Path(self.tmpdir).joinpath("greengrass-build/uat-features").exists()
        assert not uat_recipe_file.exists()

    def test_when_test_module_build_with_interpolation_and_component_not_built_then_raise_exception(self):
        self.setup_test_data_config("config.json")
        # Test
        with pytest.raises(Exception) as e:
            build_command = BuildCommand({})
            build_command.run()
        assert "Component is not built" in e.value.args[0]

    def setup_test_data_config(self, config_file):
        # Setup test data
        source = Path(self.c_dir).joinpath("integration_tests/test_data/config/").joinpath(config_file).resolve()
        shutil.copy(source, Path(self.tmpdir).joinpath("gdk-config.json"))
        shutil.unpack_archive(
            Path(self.c_dir).joinpath("integration_tests/test_data/templates/TestTemplateForCLI.zip").resolve(),
            extract_dir=Path(self.tmpdir),
        )
        shutil.move(Path(self.tmpdir).joinpath("TestTemplateForCLI"), Path(self.tmpdir).joinpath("uat-features"))
        Path(self.tmpdir).joinpath("greengrass-build/recipes").mkdir(parents=True)
