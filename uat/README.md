# End-to-end tests for Greengrass Development Kit (GDK) - Command Line Interface (CLI)

### *Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.*

End-to-end setup uses `pytest` and expects test dependencies to be installed.

### Getting Started

#### Prerequisites
1. [Python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/latest/installation/): As the GDK CLI tool is written in python, you need to have python3 and pip installed. The most recent version of python includes pip.

2. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html): As you'd have to configure your AWS credentials using AWS CLI before running certain gdk commands.

#### 1. Cloning CLI repository

To install the latest version of CLI using this git repository and pip, run the following command

```shell
git clone https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v1.1.0
cd aws-greengrass-gdk-cli
```

#### 2. Install CLI from code

```shell
python3 -m pip install pip
pip install .
```

#### 3. Configure AWS credentials

Configure AWS CLI with your credentials as shown here - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html.

#### 4. Installing test dependencies

```
pip install -r test-requirements.txt
```

#### 5. Running end-to-end test suite

```shell
pytest -v -s uat
```

### Built-in options

#### `--gdk-debug` option

Pass this flag to emit debug logs from gdk cli during all test runs. Example:
```shell
pytest -v -s uat --gdk-debug
```

#### 1. `--gdk-debug` option

Pass this flag to emit debug logs from gdk cli during all test runs. Example:
```shell
pytest -v -s uat --gdk-debug
```

#### 2. `--instrumented` option

Pass this flag to in combination with coverage to track code coverage by the test suite.
```shell
coverage run --source=gdk -m pytest -v -s uat --instrumented
```

Note: The `coverage` is required to instrument the code.

#### 3. `--target-version` option
Pass this flag to run test suite considering a specific gdk version.
```shell
pytest -v -s uat --target-version 1.1.0
```

If not provided than target version defaults to `HEAD`, which makes version constraint evaluation to assume
the tests are running against the most recent commit.

#### 4. `@pytest.mark.version(...)` constraints
`@pytest.mark.version(...)` is pytest marker to enforce version constraints for any test.

The marker takes kwargs (key & values) to define constraints. These can be combined to create upper and
lower bounds. Available key args are:
 * `eq`: equal to gdk cli version (exact version match).
 * `min` : minimum gdk cli version (lower bound)
 * `ge`: greater than or equal to gdk cli version (lower bound). Alias of `min`.
 * `gt`: greater than gdk cli version (lower bound).
 * `max` : maximum gdk cli version (upper bound)
 * `le`: less than or equal to gdk cli version (upper bound). Alias of `max`.
 * `lt`: less than gdk cli version (upper bound).

Examples:
```python
    @pytest.mark.version(eq='1.1.0')
    @pytest.mark.version(min='1.1.0') or @pytest.mark.version(ge='1.1.0')
    @pytest.mark.version(max='1.1.0') or @pytest.mark.version(le='1.1.0')
    @pytest.mark.version(gt='1.1.0')
    @pytest.mark.version(lt='1.1.0')
    @pytest.mark.version(min='1.0.0', max='1.1.0')
```


