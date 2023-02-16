# Greengrass Development Kit - Command Line Interface
![CI](https://github.com/aws-greengrass/aws-greengrass-gdk-cli/workflows/CI/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/aws-greengrass/aws-greengrass-gdk-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/aws-greengrass/aws-greengrass-gdk-cli)

### *Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.*
#### *SPDX-License-Identifier: Apache-2.0*

The AWS IoT Greengrass Development Kit Command-Line Interface (GDK CLI) provides features that help you develop custom Greengrass components. You can use the GDK CLI to create, build, and publish custom components. When you create a component repository with the GDK CLI, you can start from a template or a community component from the Greengrass Software Catalog.

Please follow the [GDK CLI public documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-development-kit-cli.html) to learn more about the available commands and configuration that GDK CLI has to offer. 

### Getting Started

#### Prerequisites
 1. [Python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/latest/installation/): As the GDK CLI tool is written in python, you need to have python3 and pip installed. The most recent version of python includes pip.

 2. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html): As you'd have to configure your AWS credentials using AWS CLI before running certain gdk commands. 

#### 1. Installing CLI

To install the latest version of CLI using this git repository and pip, run the following command

`pip3 install git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v1.1.0`

Run `gdk --help` to check if the cli tool is successfully installed.

#### 2. Configure AWS credentials

Configure AWS CLI with your credentials as shown here - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html.

#### 3. Quick start wih HelloWorld component written in python

*Note: Following steps are focused as a quick start guide. For more detailed steps, refer [our documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-components.html#create-component-gdk-cli).*

1. Initializes new project with a HelloWorld Greengrassv2 component.

`gdk component init --template HelloWorld --language python -n HelloWorld`

2. Change directory to `HelloWorld`.

`cd HelloWorld`

3. Update configuration in `gdk-config.json`
   1. Config file `gdk-config.json` would have placeholders:
   ```json
    {
        "component": {
            "com.example.JavaHelloWorld": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "NEXT_PATCH",
                "build": {
                    "build_system": "maven"
                },
                "publish": {
                    "bucket": "<PLACEHOLDER_BUCKET>",
                    "region": "<PLACEHOLDER_REGION>"
                }
            }
        },
        "gdk_version": "1.0.0"
    }
   ```
   2. Replace `<PLACEHOLDER_AUTHOR>` with your name, `<PLACEHOLDER_BUCKET>` with a s3 bucket name and `<PLACEHOLDER_REGION>` with an aws region.
   3. After replace these value the `gdk-config.json` file should look similar to:
   ```json
    {
        "component": {
            "com.example.JavaHelloWorld": {
                "author": "J. Doe",
                "version": "NEXT_PATCH",
                "build": {
                    "build_system": "maven"
                },
                "publish": {
                    "bucket": "my-s3-bucket",
                    "region": "us-east-1"
                }
            }
        },
        "gdk_version": "1.0.0"
    }
   ```

4. Build the artifacts and recipes of the component.

`gdk component build`

5. Creates new version of the component in your AWS account.

`gdk component publish`

#### 4. Local deployment for local tests

1. Build the component specifing also the gdk-config.json file, the recipe.json file and the build folder:

`gdk component build -d -c gdk-config.json -r recipe.json -u greengrass-build`

2. Push the component locally to a custom folder:

`gdk component push -u greengrass-build -e file:///tmp/gg`

1. One you have done local tests, publish component on cloud retrieving the built artifact from local folder:

`gdk component publish -d -c gdk-config.json -u /tmp/gg -n <component_name> -w <component_version>`.