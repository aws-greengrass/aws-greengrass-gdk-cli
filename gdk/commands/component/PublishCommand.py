import logging
from gdk.commands.component.transformer.PublishRecipeTransformer import PublishRecipeTransformer

import gdk.commands.component.component as component
import gdk.common.utils as utils
from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
from gdk.aws_clients.S3Client import S3Client
from gdk.commands.Command import Command
from gdk.commands.component.config.ComponentPublishConfiguration import ComponentPublishConfiguration


class PublishCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "publish")

        self.project_config = ComponentPublishConfiguration(command_args)
        self.s3_client = S3Client(self.project_config.region)
        self.greengrass_client = Greengrassv2Client(self.project_config.region)

    def run(self):
        try:
            self.try_build()
            self._publish_component_version(self.project_config.component_name, self.project_config.component_version)
        except Exception:
            logging.error(
                "Failed to publish a new version '%s' of the component '%s'.",
                self.project_config.component_version,
                self.project_config.component_name,
            )
            raise

    def try_build(self):
        # TODO: This method should just warn and proceed. It should not build the component.
        component_name = self.project_config.component_name
        logging.debug("Checking if the component '%s' is built.", component_name)
        if not utils.dir_exists(self.project_config.gg_build_component_artifacts_dir):
            logging.warning(
                "The component '%s' is not built.\nSo, building the component before publishing it.", component_name
            )
            component.build({})

    def _publish_component_version(self, component_name, component_version):
        logging.info("Publishing the component '%s' with the given project configuration.", component_name)
        logging.info("Uploading the component built artifacts to s3 bucket.")
        self.upload_artifacts_s3()

        logging.info("Updating the component recipe %s-%s.", component_name, component_version)
        PublishRecipeTransformer(self.project_config).transform()

        logging.info("Creating a new greengrass component %s-%s.", component_name, component_version)
        self.greengrass_client.create_gg_component(self.project_config.publish_recipe_file)

    def upload_artifacts_s3(self) -> None:
        """
        Uploads all the artifacts from component artifacts build folder to s3 bucket.

        Raises an exception when the request is not successful.
        """
        _bucket = self.project_config.bucket

        build_component_artifacts = list(self.project_config.gg_build_component_artifacts_dir.iterdir())

        if not build_component_artifacts:
            logging.info("No artifacts found in the component build folder. Skipping the artifact upload step")
            return

        logging.info(
            (
                "Uploading component artifacts to S3 bucket: %s. If this is your first time using this bucket, add the"
                " 's3:GetObject' permission to each core device's token exchange role to allow it to download the component"
                " artifacts. For more information, see %s."
            ),
            _bucket,
            utils.doc_link_device_role,
        )

        self.s3_client.create_bucket(_bucket)

        component_name = self.project_config.component_name
        component_version = self.project_config.component_version
        options = self.project_config.options
        s3_upload_file_args = options.get("file_upload_args", {})

        for artifact in build_component_artifacts:
            s3_file_path = f"{component_name}/{component_version}/{artifact.name}"
            logging.debug("Uploading artifact '%s' to the bucket '%s'.", artifact.resolve(), _bucket)
            self.s3_client.upload_artifact(artifact, _bucket, s3_file_path, s3_upload_file_args)
