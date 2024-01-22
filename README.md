# IDSS Engine Commons
[![Pytest](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/run-tests.yml) [![Lint with pylint](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/linter.yml/badge.svg)](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/linter.yml)

<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-92%25-brightgreen.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>idsse/common</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/aws_utils.py">aws_utils.py</a></td><td>86</td><td>5</td><td>5</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/aws_utils.py#L 94%"> 94%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/config.py">config.py</a></td><td>68</td><td>8</td><td>8</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/config.py#L 88%"> 88%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/geo_image.py">geo_image.py</a></td><td>219</td><td>14</td><td>14</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/geo_image.py#L 94%"> 94%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/grid_proj.py">grid_proj.py</a></td><td>112</td><td>2</td><td>2</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/grid_proj.py#L 98%"> 98%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/json_message.py">json_message.py</a></td><td>23</td><td>1</td><td>1</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/json_message.py#L 96%"> 96%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/log_util.py">log_util.py</a></td><td>43</td><td>3</td><td>3</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/log_util.py#L 93%"> 93%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/netcdf_io.py">netcdf_io.py</a></td><td>47</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/path_builder.py">path_builder.py</a></td><td>128</td><td>10</td><td>10</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/path_builder.py#L 92%"> 92%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/publish_confirm.py">publish_confirm.py</a></td><td>151</td><td>13</td><td>13</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/publish_confirm.py#L 91%"> 91%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/rabbitmq_utils.py">rabbitmq_utils.py</a></td><td>61</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/utils.py">utils.py</a></td><td>103</td><td>14</td><td>14</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/utils.py#L 86%"> 86%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/validate_schema.py">validate_schema.py</a></td><td>40</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/vectaster.py">vectaster.py</a></td><td>193</td><td>31</td><td>31</td><td><a href="https://github.com/NOAA-GSL/idss-engine-commons/blob/main/idsse/common/vectaster.py#L 84%"> 84%</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1274</b></td><td><b>101</b></td><td><b>92%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

## Overview
The `idss-engine-commons` project is responsible for defining all implicit common dependencies that are used by the apps that make up the IDSS Engine Project distributed system. This
repository should be used to house elements that are common across multiple projects to encourage reuse.

# Twelve-Factors
The complete twelve-factors methodologies that the IDSS Engine Project adheres to can be found in the umbrella [idss-engine](https://github.com/NOAA-GSL/idss-engine) repository. The subset of the twelve factors that follows are specifics to this app only.

## Logging
To support some standardization and best practices for IDSS Engine, developers should following the logging guide found [here](python/logging.rst)

## Build, Release, and Run
The subsections below outline how to build the common images within this project. All microservices built with Docker are done within the
[idss-engine/build](https://github.com/NOAA-GSL/idss-engine/build/) directory.

> **Recommended Tags** development `:dev` stable release `:release` ie. `:alder` targeted environment `:aws`

### Python Base Image (Basic)
---
Any python based microservice within IDSS Engine should use the following image as its base

#### Build
From the IDSS Engine project root directory `idss-engine/build/<env>/<arch>/`:

`$ docker-compose build python_base`

> **Image Name** `idsse/commons/python-base:<tag>`

### Python Base Image (Scientific)
---
Any python based microservice within IDSS Engine that requires python scientific packages (numpy, netcdf, etc) should use the following image as its base. This base image also includes common python utilities that other services can utilize. For specifics on what these utilities are, see the [README](python/idsse_common/README.md) within the `idsse_commons` directory.

#### Build
From the IDSS Engine project root directory `idss-engine/build/<env>/<arch>/`:

`$ docker-compose build python_base_sci`

> **Image Name** `idsse/commons/python-base-sci:<tag>`

### Java Base Image
---
Any java based microservices within IDSS Engine should use the following image as its base

#### Build
From the IDSS Engine project root directory `idss-engine/build/<env>/<arch>/`:

`$ docker-compose build java_base`

> **Image Name** `idsse/commons/java-base:<tag>`

### RabbitMQ Server
---
The IDSS Engine can be deployed with Docker and/or Kubernetes. If developers are deploying locally with Docker, they
can create their own RabbitMQ service as follows:

> **Developer Note** if deploying in a kubernetes cluster, it is not necessary to build this image as it will be done via a Helm Chart

#### Build
From the IDSS Engine project root directory `idss-engine/build/<env>/<arch>/`:

`$ docker-compose build rabbit_mq`

**Development Image Name** `idss.engine.commons.rabbitmq.server:<tag>`

**Packaged/Deployed Image Name** `idsse/commons/rabbitmq:<tag>`

### Couchdb Server
---
The IDSS Engine can be deployed with Docker and/or Kubernetes. If developers are deploying locally with Docker, they
can create their own RabbitMQ service as follows:

> **Developer Note** if deploying in a kubernetes cluster, it is not necessary to build this image as it will be done via a Helm Chart

#### Build
From the IDSS Engine project root directory `idss-engine/build/<env>/<arch>/`:
  
`$ docker-compose build couch_db`

**Development Image Name** `idss.engine.commons.couchbase.server:<tag>`

**Packaged/Deployed Image Name** `idsse/commons/couchdb:<tag>`

### Running IDSS Engine
See the **Build, Release, Run** section within the umbrella project documentation: [[idss-engine](https://github.com/NOAA-GSL/idss-engine)](https://github.com/NOAA-GSL/idss-engine/blob/main/README.md#running-idss-engine)
