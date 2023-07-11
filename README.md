# IDSS Engine Commons
[![Pytest](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/NOAA-GSL/idss-engine-commons/actions/workflows/run-tests.yml)

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
