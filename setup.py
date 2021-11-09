from setuptools import setup, find_packages
import codecs
from pathlib import Path

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

def read(rel_path):
    here = Path(__file__).parent.resolve()
    with codecs.open(Path(here).joinpath(rel_path).resolve(), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

long_description = 'Greengrass CLI Tool for creating Greengrass components.'

setup(
		name ='greengrass-tools',
		version = get_version("greengrassTools/_version.py"),
		author ='AWS IoT Greengrass Labs',
		author_email = '',
		url = '',
		description ='Greengrass CLI Tool for creating Greengrass components',
		long_description = long_description,
		long_description_content_type ="text/markdown",
		license ='Apache-2.0',
		packages = find_packages(),
		entry_points ={
			'console_scripts': [
				'greengrass-tools = greengrassTools.CLIParser:main'
			]
		},
		classifiers =(
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
		),
		install_requires=[requirements],
		keywords ='aws iot greengrass cli component',
		zip_safe = False,
		include_package_data = True
)
