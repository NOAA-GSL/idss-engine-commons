# Impact-based Decision Support Service Engine (IDSSe) Common Code
## idsse_common

The `idsse_common` is a location for common utilities that will be installed as a package for IDSSe micro-service deployments.

---
# Package Contents

## Config
Name: config

Contents: class Config

## Path Builder
Name: path_builder

Contents: class PathBuilder

## Publish Confirm
Name: publish_confirm

Contents: class publish_confirm

## Utilities
Name: utils

Contents: 

## Log Utilities
name: log_util

Contents:

## JSON Message
name: json_message

Content

---
# Packaging

The following sections cover the packaging, build/install and use of the IDSSe Common code.

## Python Packaging

The complete documentation for packaging python projects can be found at [Python Packaging](https://packaging.python.org/en/latest/tutorials/packaging-projects/) which outlines several ways to do 
this. The initial packaging for the project uses [setuptools](https://setuptools.pypa.io/en/latest/setuptools.html) to manage the dependencies and install

## Dependencies
---
> **Developer Note:**  It is assumed that this idsse-commons package will be part of the standard docker container installed 
> with all other required dependencies.

## Build and Install

To manually install the package on your local instance pull the data-access-service from the repository and go into idsse_common

From the project root directory `data-access-service/idsse_common`:

`$ python3 setup.py install`

## Using the package

Once installed elements from the package can be imported directly into code. For example:

---
> from idsse.common.path_builder import PathBuilder

## Running tests
### Python
After installing the project's dependencies, make sure you have the [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/config.html?highlight=missing#reference) plugin installed. 

Run pytest coverage with the following CLI command. Note: the path argument can be removed to run all tests in the project.
```
pytest --cov=python/idsse_common python/idsse_common/test --cov-report=term-missing
```
