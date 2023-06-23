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

For any of the steps below, first clone this idss-engine-commons repository locally from GitHub.

### Building this library

1. `cd` into `/python/idsse_common`
1. Build the project
    ```
    $ python3 setup.py install
    ```

**NOTE** Python 3.11+ is required to install and use this package. Install should fail for earlier versions

### Importing this library into other projects

1. `cd` into the project's directory (where you want to use this library)
1. Make sure you're command line session has a `virtualenv` created and activated
    1. If you haven't done this, run `python3 -m venv .venv`
    1. Activate the virtualenv with `source .venv/bin/activate`
1. Use `pip -e` to install the library using the local path to the cloned repo's `setup.py`. E.g.
    ```
    pip install -e /Users/my_user_name/idss-engine-commons/python/idsse_common
    ```

On success, you should see a message from pip like `Successfully built idsse-1.x`


## Using the package

Once installed, elements from the package can be imported directly into code. For example:

```
from idsse.common.path_builder import PathBuilder
my_path_builder = PathBuilder()
```

## Running tests

1. Install this library's dependencies as detailed above in [Building this library](#building-this-library)
1. Install [pytest](https://docs.pytest.org/en/latest/index.html) and the [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/config.html?highlight=missing#reference) plugin if you don't have it
    ```
    pip install pytest pytest-cov
    ```
1. Generate a pytest coverage report with the following command 
    ```
    pytest --cov --cov-report=term-missing
    ```
