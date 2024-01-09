import os
import t_utils
import shutil

from behave import step
from pathlib import Path
from constants import (
    DEFAULT_AWS_REGION, DEFAULT_S3_BUCKET_PREFIX
)


@step('we make directory {dir_name}')
def have_new_work_dir(context, dir_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    new_dir = Path(cwd).joinpath(dir_name)
    if not new_dir.exists():
        new_dir.mkdir(parents=True, exist_ok=True)
    assert new_dir.exists(), f"Directory {dir_name} does not exist in {cwd}"
    os.chdir(str(new_dir))
    context.cwd = os.getcwd()


@step('we change directory to {dir_name}')
def change_work_dir(context, dir_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    new_dir = Path(cwd).joinpath(dir_name)
    assert new_dir.exists(), f"Directory {dir_name} does not exist in {cwd}"
    os.chdir(str(new_dir))
    context.cwd = os.getcwd()


@step('set {path} to executable')
def make_executable(context, path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(path, mode)


@step('we get s3 bucket name')
def get_s3_bucket(context):
    aws_account = t_utils.get_acc_num(DEFAULT_AWS_REGION)
    context.last_s3_bucket = f"{DEFAULT_S3_BUCKET_PREFIX}-{DEFAULT_AWS_REGION}-{aws_account}"


@step('we setup gdk project {name} from s3')
def setup_project_from_s3(context, name):
    # download zip file from s3
    file = f"{name}.zip"
    unique_file = f"{name}-{t_utils.random_id()}.zip"
    aws_account = t_utils.get_acc_num(DEFAULT_AWS_REGION)
    bucket = f"{DEFAULT_S3_BUCKET_PREFIX}-{DEFAULT_AWS_REGION}-{aws_account}"
    cwd = context.cwd if "cwd" in context else os.getcwd()
    unique_file_path = Path(cwd).joinpath(unique_file).resolve()

    s3_client = context.s3_client if "s3_client" in context else t_utils.create_s3_client(DEFAULT_AWS_REGION)
    s3_client.download_file(bucket, file, str(unique_file_path))
    assert unique_file_path.exists(), f"Couldn't find the downloaded {file} at {unique_file_path}"

    # unpack zip file
    shutil.unpack_archive(
        Path(unique_file_path),
        Path(cwd).resolve(),
        "zip",
    )

    # change working dir
    new_dir = Path(cwd).joinpath(name)
    assert new_dir.exists(), f"Directory {name} does not exist in {cwd}"
    os.chdir(str(new_dir))
    context.cwd = os.getcwd()
