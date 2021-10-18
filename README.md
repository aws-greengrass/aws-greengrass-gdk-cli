
## Build the tool
```
python3 setup.py install 
python3 setup.py sdist bdist_wheel 
pip3 install dist/ggt-1.0.0-py3-none-any.whl --force-reinstall 
```

After installing ggt, run commands like
```
ggt --help
ggt component --help
ggt component init --help
```

## Testing

```
pip3 install pytest coverage
```

From the root folder, run

```coverage run --source=ggtools -m pytest -v -s tests && coverage report --show-missing```