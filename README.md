# IDSS Engine Commons
## idss-engine-commons

The `idss-engine-commons` is responsible for defining all implicit common dependencies that are used by the apps that make up the IDSS Engine Project distributed system.

---
# Twelve-Factors

The complete twelve-factors methodologies that the IDSS Engine Project adheres to can be found in the umbrella [idss-engine](https://github.com/NOAA-GSL/idss-engine) repository. The subset of the twelve factors that follows are specifics to this app only.

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

`$ ./gradlew build` will produce a jar file: `idss-engine-commons/java/build/libs/idss-engine-common-1.0.jar`

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

