
## Installing gdk CLI

Use the following commands to install `gdk` cli inside a virtual environment. Replace `<venv-name>` with name of the virtual enviroment you want to create. 

1. Install virtual env module.

    `python3 -m pip install --user virtualenv` 

2. Creating a virtual environment called venv-name

    `python3 -m venv <venv-name> `  

3. Activating venv-name virtual env

    `source <venv-name>/bin/activate` 

4. Installing cli tool.

    `pip3 install git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git`

