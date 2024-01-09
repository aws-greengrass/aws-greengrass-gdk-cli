import os
import re
import tempfile
import t_utils

from behave import fixture, use_fixture
from pathlib import Path
from packaging.version import parse as version_parser
from t_setup import GdkProcess, GdkInstrumentedProcess
from steps.constants import (
    GG_BUILD_DIR,
    DEFAULT_AWS_REGION
)

# ------------------------------------------------------------------------
# FIXTURES
# ------------------------------------------------------------------------


@fixture
def gdk_cli(context):
    instrumented = context.config.userdata.getbool("instrumented", False)
    debug = context.config.userdata.getbool("gdk-debug", False)
    print(f"Initializing GDK client{' in debug mode' if debug else ''}{' with instrumented code.' if debug else '.'}")
    # SETUP FIXTURE
    if instrumented:
        context.gdk_cli = GdkInstrumentedProcess(debug)
    else:
        context.gdk_cli = GdkProcess(debug)
    # USE FIXTURE
    yield context.gdk_cli
    # CLEANUP
    context.gdk_cli = None


@fixture
def change_working_dir(context, **kwargs):
    old_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory(suffix=None, prefix=None, dir=None) as new_dir:
            if kwargs and 'name' in kwargs.keys():
                dir_name = kwargs.get('name', None)
                if dir_name:
                    new_dir = Path(new_dir.name).joinpath(dir_name)
                    new_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(str(new_dir))
            context.cwd = os.getcwd()
            print(f"Created new working directory at {context.cwd}")
            yield new_dir
        print(f"Cleaning temp directory at {new_dir}")
    except Exception as err:
        print(f"Error while working directory setup/cleanup: \n{err}")
    finally:
        # CLEANUP
        os.chdir(str(old_cwd))


@fixture()
def version_constraint(context, **kwargs):
    version_option = context.config.userdata.get("target-version", "HEAD")
    if version_option is None:
        return

    latest_mode = version_option == 'HEAD'
    print(f"\nTarget gdk-cli version {version_option}")

    # parse target version from options
    target_version = version_parser(version_option) if not latest_mode else version_option

    scenario = context.scenario

    # if used as @version(eq=1.0.0)
    eq_version = kwargs.get('eq')
    eq_version = version_parser(eq_version) if eq_version else None
    if eq_version and (latest_mode or target_version == eq_version):
        scenario.skip(f'Target version {target_version} is not equal to the required version {eq_version}.')

    # if used as @version(lt=1.0.0)
    lt_version = kwargs.get('lt')
    lt_version = version_parser(lt_version) if lt_version else None
    if lt_version and (latest_mode or target_version >= lt_version):
        scenario.skip(f'Target version {target_version} is not lower than required version {lt_version}.')

    # if used as @version(min=1.0.0) or as @pytest.mark.version(le=1.0.0)
    le_version = kwargs.get('le')
    max_version = le_version if le_version else kwargs.get('max')
    max_version = version_parser(max_version) if max_version is not None else None
    if max_version and (latest_mode or target_version > max_version):
        scenario.skip(f'Target version {target_version} is higher than required version {max_version}.')

    # if used as @version(gt=1.0.0)
    gt_version = kwargs.get('gt')
    gt_version = version_parser(gt_version) if gt_version else None
    if not latest_mode and gt_version and target_version <= gt_version:
        scenario.skip(f'Target version {target_version} is not greater than required version {gt_version}.')

    # if used as @version(min=1.0.0) or as @version(ge=1.0.0)
    ge_version = kwargs.get('ge')
    min_version = ge_version if ge_version else kwargs.get('min', '1.0.0')
    min_version = version_parser(min_version) if min_version else None
    if not latest_mode and min_version and target_version < min_version:
        scenario.skip(f'Target version {target_version} is lower than required version {min_version}.')

# ------------------------------------------------------------------------
# FIXTURE REGISTRIES USED BY HOOKS
# ------------------------------------------------------------------------


registry_auto_use_fixtures = [
    gdk_cli
]

registry_use_by_tag_fixtures = {
    "version": version_constraint,
    "change_cwd": change_working_dir
}

# ------------------------------------------------------------------------
# HOOKS
# ------------------------------------------------------------------------


def before_tag(context, tag):
    __tag = tag
    __kvargs = dict()
    if '(' in tag:
        matcher = re.match(r'^([a-zA-Z_\-0-9]*)\((.*)\)$', tag)
        __tag = matcher.group(1)
        __args = matcher.group(2)
        matches = re.findall(r'([a-zA-Z_\-0-9]*)=[\'"]([^,\'"]*)[\'"]', __args)
        for match in matches:
            __kvargs[match[0]] = match[1]

    # get fixture from registry
    func = registry_use_by_tag_fixtures.get(__tag, None)
    if callable(func):
        use_fixture(func, context, **__kvargs)


def before_scenario(context, scenario):
    for _fixture in registry_auto_use_fixtures:
        if callable(_fixture):
            use_fixture(_fixture, context)


def before_all(context):
    context.config.setup_logging()


def after_scenario(context, scenario):
    if "last_component" in context and "last_cli_command_type" in context:
        command_type = context.last_cli_command_type
        if command_type == "component publish":
            component_name = context.last_component
            cwd = context.cwd if "cwd" in context else os.getcwd()
            recipes_path = Path(cwd).joinpath(GG_BUILD_DIR).joinpath("recipes").resolve()
            t_utils.clean_up_aws_resources(
                component_name, t_utils.get_version_created(recipes_path, component_name), DEFAULT_AWS_REGION
            )
