# Conda base image
ARG conda_alpine_version
FROM continuumio/miniconda3:"${conda_alpine_version}"

ARG maintainer
ARG openjdk_version

LABEL maintainer "${maintainer}"

# Setup conda ENV
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

COPY ./requirements.txt requirements.txt

# Install core dependencies
RUN conda config --add channels conda-forge && \
    conda install -y --file requirements.txt && \
    conda install openjdk="${openjdk_version}" && \
    conda clean -y --all

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade
# Install any specific packages via apk (alpine package keeper)
#RUN apk add --no-cache \
#    apk-tools=2.12.7-r0

# Get the latest package updates to keep security vulnerabilties down
RUN pip install --upgrade wheel setuptools