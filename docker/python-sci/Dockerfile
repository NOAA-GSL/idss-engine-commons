FROM continuumio/miniconda3:26.1.1
# miniconda:26.1.1 uses python 3.13.12

ARG maintainer
LABEL maintainer=${maintainer}

# Setup ENV
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV SHELL=/bin/bash
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

# Get latest packages before installing dependencies to
# help keep security vulnerabilities down
RUN conda update --all

# Install dependencies
RUN conda config --set solver classic && \
    conda config --add channels conda-forge && \
    conda config --remove channels defaults && \
    conda config --set channel_priority strict && \
    conda install -n base conda-libmamba-solver && \
    conda config --set solver libmamba && \
    conda install -y \
    pika==1.3.1 \
    python-dateutil==2.9.0 \
    pint==0.25 \
    numpy==2.4.2 \
    netcdf4==1.7.4 \
    h5netcdf==1.8.1 \
    h5py==3.15.1 \
    zarr==3.1.5 \
    dask==2026.1.2 \
    xarray==2026.2.0 \
    pcodec==1.0.1 \
    pygrib==2.1.8 \
    pyproj==3.7.2 \
    awscli==2.34.7 \
    jsonschema==4.25.1 \
    s5cmd==2.2.2 \
    geojson==3.2.0 \
    shapely==2.1.2 \
    pillow==12.1.1 \
    flask==3.1.3 \
    gunicorn==25.1.0 \
    python-logging-rabbitmq==2.0.0 \
    scipy==1.17.1 \
    && conda clean -y --all

# Get the latest package updates to keep security vulnerabilities down
#RUN apk update && apk upgrade # This is for alpine, but we are using miniconda which is debian based, so we use conda update --all instead

# Install idsse common python code
WORKDIR /python/idsse_common

COPY ./python/idsse_common /python/idsse_common

RUN python /python/idsse_common/setup.py install
