from unittest import TestCase
import pytest
from pathlib import Path
import os
import shutil
from gdk.commands.component.BuildCommand import BuildCommand
import json
import platform
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile
import boto3
from botocore.stub import Stubber


class ComponentBuildCommandIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        os.chdir(self.tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_GIVEN_zip_build_system_WHEN_build_THEN_build_zip_artifacts(self):
        self.zip_test_data()
        bc = BuildCommand({})
        bc.run()
        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/" + self.tmpdir.name + ".zip").exists()
        assert build_recipe_file.exists()

        with open(build_recipe_file, "r") as f:
            assert f"s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/{self.tmpdir.name}.zip" in f.read()

    def test_GIVEN_zip_build_system_WHEN_build_and_artifacts_not_on_s3_THEN_build_raises_exception(self):
        self.zip_test_data()
        content = CaseInsensitiveRecipeFile().read(self.tmpdir.joinpath("recipe.yaml"))
        artifacts = content["Manifests"][0]["Artifacts"]
        artifacts.append({"URI": "s3://some/s3/bucket/abc.txt"})
        CaseInsensitiveRecipeFile().write(self.tmpdir.joinpath("recipe.yaml"), content)

        bc = BuildCommand({})

        with pytest.raises(Exception) as e:
            bc.run()

        assert "Could not find artifact with URI 's3://some/s3/bucket/abc.txt' on s3 or inside the build folders." in str(
            e.value.args[0]
        )
        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/" + self.tmpdir.name + ".zip").exists()
        assert not build_recipe_file.exists()

    def test_GIVEN_maven_build_system_WHEN_build_with_artifacts_on_s3_THEN_build_succeeds(self):
        # Prepare test data
        self.maven_test_data()
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/maven/pom.xml"),
            self.tmpdir.joinpath("pom.xml"),
        )
        content = CaseInsensitiveRecipeFile().read(self.tmpdir.joinpath("recipe.yaml"))
        artifacts = content["Manifests"][0]["Artifacts"]
        artifacts.append({"URI": "s3://some/s3/bucket/abc.txt"})
        CaseInsensitiveRecipeFile().write(self.tmpdir.joinpath("recipe.yaml"), content)

        # Prepare s3 stub
        client = boto3.client("s3", region_name="us-east-1")
        self.mocker.patch("boto3.client", return_value=client)
        s3_client_stub = Stubber(client)
        s3_client_stub.add_response(
            "head_object",
            {"ResponseMetadata": {"HTTPStatusCode": 200}, "ContentLength": 100},
            {"Bucket": "some", "Key": "s3/bucket/abc.txt"},
        )
        s3_client_stub.activate()

        # WHEN
        bc = BuildCommand({})
        bc.run()

        # THEN
        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/HelloWorld-1.0.0.jar").exists()
        assert build_recipe_file.exists()

        with open(build_recipe_file, "r") as f:
            content = f.read()
            assert "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/HelloWorld-1.0.0.jar" in content
            assert "s3://some/s3/bucket/abc.txt" in content

    def test_GIVEN_maven_build_system_WHEN_build_THEN_build_jar_artifacts(self):
        self.maven_test_data()
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/maven/pom.xml"),
            self.tmpdir.joinpath("pom.xml"),
        )
        bc = BuildCommand({})
        bc.run()

        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/HelloWorld-1.0.0.jar").exists()
        assert build_recipe_file.exists()

        with open(build_recipe_file, "r") as f:
            content = f.read()
            assert "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/HelloWorld-1.0.0.jar" in content

    def test_GIVEN_maven_build_system_WHEN_exception_in_build_THEN_raise_exception(self):
        self.maven_test_data()

        bc = BuildCommand({})
        with pytest.raises(Exception) as e:
            bc.run()
        if platform.system() == "Windows":
            assert "['mvn.cmd', 'package']" in str(e)
        else:
            assert "['mvn', 'package']" in str(e)
        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert not self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/HelloWorld-1.0.0.jar").exists()
        assert not build_recipe_file.exists()

    def test_GIVEN_custom_build_system_WHEN__build_THEN_run_custom_build_command(self):
        self.custom_test_data()

        bc = BuildCommand({})
        bc.run()

        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/").exists()
        assert not build_recipe_file.exists()

    def test_GIVEN_gdk_project_with_oversized_recipe_file_WHEN_build_THEN_raise_exception(self):
        self.zip_test_data_oversized_recipe()
        bc = BuildCommand({})
        with pytest.raises(Exception) as e:
            bc.run()
        assert "Please make sure it does not exceed 16kB (16000 bytes) and try again" in str(e)

        build_recipe_file = self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml").resolve()
        assert not build_recipe_file.exists()

    def zip_test_data(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config/config.json"), self.tmpdir.joinpath("gdk-config.json")
        )

        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/recipes/hello_world_recipe.yaml"),
            self.tmpdir.joinpath("recipe.yaml"),
        )
        with open(self.tmpdir.joinpath("recipe.yaml"), "r") as f:
            recipe = f.read()
            recipe = recipe.replace("$GG_ARTIFACT", self.tmpdir.name + ".zip")

        with open(self.tmpdir.joinpath("recipe.yaml"), "w") as f:
            f.write(recipe)

        self.tmpdir.joinpath("hello_world.py").touch()

    def zip_test_data_oversized_recipe(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config/config.json"), self.tmpdir.joinpath("gdk-config.json")
        )

        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/recipes/hello_world_recipe_really_big.yaml"),
            self.tmpdir.joinpath("recipe.yaml"),
        )
        with open(self.tmpdir.joinpath("recipe.yaml"), "r") as f:
            recipe = f.read()
            recipe = recipe.replace("$GG_ARTIFACT", self.tmpdir.name + ".zip")

        with open(self.tmpdir.joinpath("recipe.yaml"), "w") as f:
            f.write(recipe)

        self.tmpdir.joinpath("hello_world.py").touch()

    def maven_test_data(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config/config.json"), self.tmpdir.joinpath("gdk-config.json")
        )
        gdk_config = self.tmpdir.joinpath("gdk-config.json")
        with open(gdk_config, "r") as f:
            config = f.read()
            config = config.replace("zip", "maven")

        with open(gdk_config, "w") as f:
            f.write(config)

        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/recipes/hello_world_recipe.yaml"),
            self.tmpdir.joinpath("recipe.yaml"),
        )

        with open(self.tmpdir.joinpath("recipe.yaml"), "r") as f:
            recipe = f.read()
            recipe = recipe.replace("$GG_ARTIFACT", "HelloWorld-1.0.0.jar")

        with open(self.tmpdir.joinpath("recipe.yaml"), "w") as f:
            f.write(recipe)

    def custom_test_data(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config/config.json"), self.tmpdir.joinpath("gdk-config.json")
        )

        gdk_config = self.tmpdir.joinpath("gdk-config.json")
        with open(gdk_config, "r") as f:
            config = json.loads(f.read())
            config_comp = config["component"]["abc"]
            config_comp.update({"build": {"build_system": "custom", "custom_build_command": "whoami"}})

        with open(gdk_config, "w") as f:
            f.write(json.dumps(config))

        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/recipes/hello_world_recipe.yaml"),
            self.tmpdir.joinpath("recipe.yaml"),
        )
