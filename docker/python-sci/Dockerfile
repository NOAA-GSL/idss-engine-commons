FROM continuumio/miniconda3:23.3.1-0-alpine

ARG maintainer
LABEL maintainer ${maintainer}

# Setup ENV
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install dependencies (and force Python 3.11 update)
RUN conda config --add channels conda-forge && \
    conda install -y python=3.11 && \
    conda install -y \
    pika==1.3.1 \
    python-dateutil==2.8.2 \
    pint==0.21 \
    numpy==1.24.3 \
    netcdf4==1.6.3 \
    h5netcdf==1.1.0 \
    pygrib==2.1.4 \
    && conda clean -y --all

# TODO python-base-sci needs to package these common elements

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade