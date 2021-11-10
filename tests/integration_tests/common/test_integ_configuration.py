import greengrassTools.common.consts as consts
import greengrassTools.common.utils as utils

def test_get_static_file_path_cli_schema():
    ## Integ test for the existence of command model file even before building the cli tool.
    model_file_path=utils.get_static_file_path(consts.config_schema_file)
    assert model_file_path is not None
    assert model_file_path.exists()