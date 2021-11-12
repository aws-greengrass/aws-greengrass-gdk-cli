import json

import greengrassTools.common.consts as consts
import greengrassTools.common.utils as utils
import jsonschema


def test_builds_config_with_schema():
    # Integ test for the existence of command model file even before building the cli tool.
    builds_file = utils.get_static_file_path(consts.project_build_system_file)
    project_build_schema = utils.get_static_file_path(consts.project_build_schema_file)
    assert project_build_schema.exists()
    assert builds_file.exists()

    with open(builds_file, "r") as f:
        data = json.loads(f.read())

    with open(project_build_schema, "r") as schemaFile:
        schema = json.loads(schemaFile.read())
    jsonschema.validate(data, schema)
