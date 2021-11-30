# Greengrass Development Kit - Command Line Interface
![CI](https://github.com/aws-greengrass/aws-greengrass-gdk-cli/workflows/CI/badge.svg?branch=main)

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

`pip3 install git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git`

Run `gdk --help` to check if the cli tool is successfully installed.

#### 2. Configure AWS credentials

Configure AWS CLI with your credentials as shown here - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html.

#### 3. Quick start wih HelloWorld component written in python

1. Initializes the project directory with a HelloWorld Greengrassv2 component. 

`gdk component init --template HelloWorld --language python`

2. Build the artifacts and recipes of the component. 

`gdk component build`

3. Creates new version of the component in your AWS account. 

`gdk component publish`
