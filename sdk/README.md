<h1 align="center">rAPId-sdk</h1>

<p align="center">
<a>
<img src="https://github.com/no10ds/rapid-api/actions/workflows/main.yml/badge.svg">
</a>
<a href="https://pypi.org/project/rapid-sdk" target="_blank">
<img src="https://img.shields.io/pypi/v/rapid-sdk?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
</p>

# About
Please see the [docs page](https://rapid-sdk.readthedocs.io/en/latest/) for greater reference.

rAPId-sdk is a Python wrapper for the rapid-api repository. It provides a simple and intuitive interface for accessing the functionality of the rapid-api library in Python.

# Contributing

To install rAPId sdk, you will need to have pyenv and python installed. You can use the provided Makefile to set up the required dependencies and create a virtual environment for the project:

```
make setup
```

This will install pyenv and the specified version of python, create a virtual environment for the project, and install the required dependencies.

To create a test deployment and upload the package to testpypi run `make deploy/test`

# Releasing

To perform a new release of the sdk see the guide below.

## Context

Performing a release involves tagging a new version of the sdk with the specific verison number.

## Steps

1. Decide on the new version number following the [semantic versioning approach](https://semver.org/)
2. Update and commit the [Changelog](./CHANGELOG.md) (you can follow the [template](./changelog_release_template.md))
3. Update the version number in `setup.py` and commit this.
4. Finally update the ReadTheDocs contents by running `make documentation/build` and then commit this.
4. Run `make release commit=<commit_hash> version=vX.X.X`

> ⚠️ Ensure the version number follows the format `vX.X.X` with full-stops in the same places.

Now the release pipeline will run automatically and build the sdk off that version of the code and finally push it to PyPi.

# License

rAPId api is released under the MIT License.
