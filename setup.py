import codecs
from pathlib import Path

from setuptools import find_packages, setup

requirements_file = "requirements.txt"
author = "AWS IoT Greengrass Labs"
email = "greengrass-labs@amazon.com"
url = "https://aws.amazon.com/greengrass/"
short_description = "Greengrass tools CLI for developing greengrass components."
long_description = "Greengrass CLI Tool for creating Greengrass components."
version_file = "gdk/_version.py"
cli_name = "gdk"
key_words = "aws iot greengrass cli component"
license = "Apache-2.0"
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Natural Language :: English",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
]
entry_points = {"console_scripts": ["gdk = gdk.CLIParser:main"]}


def get_requirements():
    with open(requirements_file, "r", encoding="utf-8") as f:
        return f.read()


def read(rel_path):
    here = Path(__file__).parent.resolve()
    with codecs.open(Path(here).joinpath(rel_path).resolve(), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name=cli_name,
    version=get_version(version_file),
    author=author,
    author_email=email,
    url=url,
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    packages=find_packages(include=["gdk", "gdk.*"]),
    entry_points=entry_points,
    classifiers=classifiers,
    install_requires=get_requirements(),
    keywords=key_words,
    zip_safe=False,
    include_package_data=True,
)
