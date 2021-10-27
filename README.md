
## Build the tool
```
pip3 install jsonschema
pip3 install requests
pip3 install pyyaml
pip3 install subprocess
python3 setup.py install 
python3 setup.py sdist bdist_wheel 
pip3 install dist/greengrass_tools-1.0.0-py3-none-any.whl --force-reinstall 
```

After installing greengrass-tools, run commands like
```
greengrass-tools --help
greengrass-tools component --help
greengrass-tools component init --help
```

## Testing

```
pip3 install pytest coverage
```

From the root folder, run

```coverage run --source=greengrassTools -m pytest -v -s tests && coverage report --show-missing```