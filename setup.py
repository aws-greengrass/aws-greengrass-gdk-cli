from setuptools import setup, find_packages

# with open('requirements.txt') as f:
# 	requirements = f.readlines()

long_description = 'Greengrass CLI Tool for creating Greengrass components.'

setup(
		name ='greengrass-tools',
		version ='1.0.0',
		author ='AWS IoT Greengrass Labs',
		author_email ='nukai@amazon.com',
		url ='',
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
		keywords ='aws iot greengrass cli component',
		zip_safe = False,
		include_package_data = True
)
