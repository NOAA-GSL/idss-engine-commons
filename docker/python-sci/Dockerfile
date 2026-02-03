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

# Get latest packages before installing dependencies to
# help keep security vulnerabilities down
RUN conda update --all

# Install dependencies (and force Python 3.12.1 update)
RUN conda config --set solver classic && \
    conda config --add channels conda-forge && \
    conda config --remove channels defaults && \
    conda config --set channel_priority strict && \
    conda install -y python=3.12.1 && \
    conda install -y \
    pika==1.3.1 \
    python-dateutil==2.9.0 \
    pint==0.25 \
    numpy==1.26.4 \
    netcdf4==1.7.3 \
    h5netcdf==1.7.3 \
    pygrib==2.1.6 \
    pyproj==3.7.2 \
    awscli==1.42.60 \
    jsonschema==4.25.1 \
    s5cmd=2.3.0 \
    geojson==3.2.0 \
    shapely==2.1.2 \
    pillow==10.4.0 \
    flask==2.3.3 \
    gunicorn==22.0.0 \
    python-logging-rabbitmq==2.0.0 \
    scipy==1.16.3 \
    && conda clean -y --all

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade

# Install idsse common python code
WORKDIR /python/idsse_common

COPY ./python/idsse_common /python/idsse_common

RUN python /python/idsse_common/setup.py install