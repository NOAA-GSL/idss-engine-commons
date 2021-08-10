# IDSS Engine Commons
## idss-engine-commons

The `idss-engine-commons` is responsible for defining all implicit common dependencies that are used by the apps that make up the IDSS Engine Project distributed system.

---
# Twelve-Factors

The complete twelve-factors methodologies that the IDSS Engine Project adheres to can be found in the umbrella [idss-engine](https://github.com/NOAA-GSL/idss-engine) repository. The subset of the twelve factors that follows are specifics to this app only.

## Logging
---
To support some standardization and best practices for IDSS Engine, developers should utilize the [idss-engine-commons logging](https://github.com/NOAA-GSL/idss-engine-commons) Java and python packages.

The general guidelines for logging are as follows:

1. All log messages shall be written to `stdout`
2. Use appropriate log levels:

| Level | Usage |
|-|-|
|`DEBUG`|Coarse and fine-grained informational events that are useful for debugging an application as well as highlighting the progress of the application as it executes.|
|`INFO`|Coarse-grained informational events that are particularly useful for communicating health and status of IDSS Engine to system administrators and users|
|`WARN`|Designates potentially harmful situations of an application that should be recorded but don't necessarily have an impact in the execution of code|
|`ERROR`|Designates severe error events that will presumably lead the application to fail.|

3. All log messages shall be written to a shared RabbitMQ exchange. See the IDSS Engine [Status](https://github.com/NOAA-GSL/engine-status) project for information on how to use the service.
4. Use the following structure for all log messages so that they can be parsed by the [Status](https://github.com/NOAA-GSL/engine-status) service:

>
> System Identifier (SID): `UUID:source:issuehour:issuemin:service;message`
> Where issue (hour/min) are UTC

**Examples:**


The IMS Request service received a new event criteria definition:

> `INFO: 529c9038-c3ba-11eb-8529-0242ac130003:ims:12:00:imsrequest;Recieved new event criteria definition: winter-wx at BOU`

The Data Manager was unable to find all forecast data:

> `ERROR: 529c9038-c3ba-11eb-8529-0242ac130003:ims:12:00:datamanager;No forecast data found for NBM on 061220210600 originating from AWS`

## Build, Release, and Run

### Python Microservices Base Image
---
Any python based microservice within IDSS Engine should use this image as it's base.

> **Image Name** `idss.engine.commons.python.service`

> **Recommended Tags** development `:dev` stable release `:major.minor` ie. `:1.0` targeted environment `:aws`

#### Build
From the project root directory `idss-engine-commons`:

`$ docker build -t idss.engine.commons.python.service:<tag> -f ./python/service/docker/Dockerfile .`

### Java Commons
---

#### Build
From the `idss-engine-commons/java` directory:

`$ ./gradlew build` will produce a jar file: `idss-engine-commons/java/build/libs/idss-engine-commons-1.0.jar`

### RabbitMQ Server
---

` idss.engine.commons.rabbitmq.server:<tag>`

> **Recommended Tags** development `:dev` stable release `:major.minor` ie. `:1.0` targeted environment `:aws` test `:test`
From the `idss-engine-commons/rabbitmq` directory:

#### Build

`$ docker build -t idss.engine.commons.rabbitmq.server:<tag> .`

#### Run

**Required arguments**:
> ```
> -e RABBITMQ_USER=<RabbitMQ default user>
> -e RABBITMQ_PASSWORD=<RabbitMQ default password>
> ```

**Developer Note**

Should look in to moving `RABBITMQ_USER` and `RABBITMQ_PASSWORD` to either configuration service or using `docker secrets`

**Optional arguments**

Use `--name` if running on a container network

> ```
> --network <network>
> --rm
> --name <host name (used by other containers as a name for connection)>
> -p 15672:15672 (for web ui mananagement console)
> ```

Examples:

`$ docker run --rm --name rmqtest --network idss_test -e RABBITMQ_USER=idss -e RABBITMQ_PASSWORD=password -p 15672:15672 idss.engine.commons.rabbitmq.server:<tag>`

URLs:

Using the port mapping `-p 15672:15672` allows access to the RabbitMQ Web UI Management Console: http://localhost:15672/

