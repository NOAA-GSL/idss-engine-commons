# Conda base image
FROM continuumio/miniconda3:4.10.3-alpine

ARG maintainer

LABEL maintainer "${maintainer}"

# Setup conda ENV
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install core dependencies
RUN conda config --add channels conda-forge && \
    conda install \
    openjdk=8 \
    pillow=9.3.0 \
    numpy=1.22.3 \
    netcdf4=1.6.2 \
    h5netcdf=1.1.0 \
    awscli=1.27.60 && \
    conda clean -y --all

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade
# Install any specific packages via apk (alpine package keeper)
#RUN apk add --no-cache \
#    apk-tools=2.12.7-r0

# Get the latest package updates to keep security vulnerabilties down
RUN pip install --upgrade wheel setuptools