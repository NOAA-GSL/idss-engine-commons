# IDSS Engine Commons
[![Pytest](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/run-tests.yml) [![Lint with pylint](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/linter.yml/badge.svg)](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/linter.yml)

<!-- Pytest Coverage Comment:Begin -->
<!-- pytest-coverage-comment --><p><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-89%25-green.svg" /></a></p><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>idsse/common</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/aws_utils.py">aws_utils.py</a></td><td>27</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/boto3_utils.py">boto3_utils.py</a></td><td>81</td><td>31</td><td>31</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/boto3_utils.py#L 62%"> 62%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/config.py">config.py</a></td><td>69</td><td>5</td><td>5</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/config.py#L 93%"> 93%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/http_utils.py">http_utils.py</a></td><td>40</td><td>4</td><td>4</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/http_utils.py#L 90%"> 90%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/json_message.py">json_message.py</a></td><td>24</td><td>1</td><td>1</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/json_message.py#L 96%"> 96%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/log_util.py">log_util.py</a></td><td>41</td><td>3</td><td>3</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/log_util.py#L 93%"> 93%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/path_builder.py">path_builder.py</a></td><td>211</td><td>22</td><td>22</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/path_builder.py#L 90%"> 90%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/protocol_utils.py">protocol_utils.py</a></td><td>93</td><td>4</td><td>4</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/protocol_utils.py#L 96%"> 96%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/rabbitmq_rpc.py">rabbitmq_rpc.py</a></td><td>110</td><td>2</td><td>2</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/rabbitmq_rpc.py#L 98%"> 98%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/rabbitmq_utils.py">rabbitmq_utils.py</a></td><td>226</td><td>31</td><td>31</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/rabbitmq_utils.py#L 86%"> 86%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/utils.py">utils.py</a></td><td>189</td><td>25</td><td>25</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/utils.py#L 87%"> 87%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/validate_schema.py">validate_schema.py</a></td><td>40</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>idsse/common/sci</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/bit_pack.py">bit_pack.py</a></td><td>85</td><td>3</td><td>3</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/bit_pack.py#L 96%"> 96%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/geo_image.py">geo_image.py</a></td><td>235</td><td>17</td><td>17</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/geo_image.py#L 93%"> 93%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/grid_proj.py">grid_proj.py</a></td><td>142</td><td>7</td><td>7</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/grid_proj.py#L 95%"> 95%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/netcdf_io.py">netcdf_io.py</a></td><td>69</td><td>38</td><td>38</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/netcdf_io.py#L 45%"> 45%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/utils.py">utils.py</a></td><td>31</td><td>7</td><td>7</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/utils.py#L 77%"> 77%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/vectaster.py">vectaster.py</a></td><td>189</td><td>17</td><td>17</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/sci/vectaster.py#L 91%"> 91%</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1902</b></td><td><b>217</b></td><td><b>89%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

## Overview
The `idss-engine-commons` project is responsible for defining all implicit common dependencies that are used by the apps that make up the IDSS Engine Project distributed system. This
repository should be used to house elements that are common across multiple projects to encourage reuse.

## Twelve-Factors
The complete twelve-factors methodologies that the IDSS Engine Project adheres to can be found in the umbrella [idss-engine](https://github.com/NOAA-GSL/idss-engine) repository. The subset of the twelve factors that follows are specifics to this app only.

## Logging
To support some standardization and best practices for IDSS Engine, developers should following the logging guide found [here](python/logging.rst)

## Contributing
Clone this repository.

Create a Python pip environment and activate it:
```sh
python3 -m venv .venv && source .venv/bin/activate
```

Install all Python dependencies based on what is installed in any of the GitHub Actions in `.github/workflows`, e.g. `linter.yml`.
```sh
pip install <libs_from_.github/workflows/linter.yml>
```

If you intend to run unit tests, you'll need to clone the [idsse-testing](https://github.com/NOAA-GSL/idsse-testing) GitHub repository, then install it as an "editable" (a.k.a. local) pip package:
```sh
pip install -e <path_to_idsse_testing_clone>/python
```

### Formatting
Python code is formatted according to the [black](https://black.readthedocs.io/) style guide, and any Pull Requests will be checked against this styling to ensure the new code has been auto-formatted.

To have `black` reformat all Python code every time you create a git commit, install the [pre-commit](https://pre-commit.com/) library:
```sh
pip install pre-commit
```

And run this to have any Git pre-commit hooks installed for you according to `.pre-commit.config.yaml`:
```sh
pre-commit install
```

If you prefer, you can install the `black` library and run it yourself manually (not running on `git commit`):
```sh
pip install black
```

This will reformat all your Python files for you:
```sh
black . --line-length 99
```

## Build, Release, and Run

The common images and packages within this project are built automatically by the project's GitHub Actions workflows using GitHub-hosted runners. **No local or manual builds are necessary.**

All common image build processes are managed through GitHub Actions and the associated configurations within the [idss-engine-commons/docker](https://github.com/NOAA-GSL/idss-engine/tree/main/docker/) directory.

### Python Base Image (Basic)
---

Any Python-based microservice within IDSS Engine should use the following image as its base.

**Image Name:** `ghcr.io/noaa-gsl/idss/commons/python/python-base:<semver>`

### Python Base Image (Scientific)
---

Any Python-based microservice within IDSS Engine that requires scientific Python packages (NumPy, NetCDF, etc.) should use this image as its base. This image also includes common Python utilities that other services can utilize. For specifics on these utilities, see the [README](python/idsse_common/README.md) within the `idsse_commons` directory.

**Image Name:** `ghcr.io/noaa-gsl/idss/commons/python/python-sci:<semver>`

**Note:** Both images are built and published through GitHub Actions. Developers do not need to run Docker Compose build commands or manually build these images locally.

### Running IDSS Engine
See the **Build, Release, Run** section within the umbrella project documentation: [[idss-engine](https://github.com/NOAA-GSL/idss-engine)](https://github.com/NOAA-GSL/idss-engine/blob/main/README.md#running-idss-engine)
