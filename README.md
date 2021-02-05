# IDSS Engine Commons
## idss-engine-commons

The `idss-engine-commons` is responsible for defining all implicit common dependencies that are used by the apps that make up the IDSS Engine Project distributed system.

---
# Twelve-Factors

The complete twelve-factors methodologies that the IDSS Engine Project adheres to can be found in the umbrella [idss-engine](https://github.com/NOAA-GSL/idss-engine) repository. The subset of the twelve factors that follows are specifics to this app only.

## 5. Build, Release, and Run

### Python Microservices Base Image
Any python based microservice within IDSS Engine should use this image as it's base.
> **Image Name** `idss.engine.commons.service`
> **Recommended Tags** development `:dev` stable release `:major.minor` ie. `:1.0` targeted environment `:aws`
#### Build
`$ cd python/microservice/docker`
`$ docker build -t idss.engine.commons.service:dev .` 
