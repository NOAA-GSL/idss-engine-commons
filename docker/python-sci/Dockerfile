FROM continuumio/miniconda3:23.3.1-0-alpine

ARG maintainer
LABEL maintainer ${maintainer}

COPY ./docker/python-sci/requirements.txt .

# Setup ENV
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install dependencies (and force Python 3.11 update)
RUN conda config --add channels conda-forge && \
    conda install python=3.11 && \
    conda install -y --file requirements.txt && \ 
    conda clean -y --all

# PIP install required dependencies
RUN pip3 install --no-cache -r requirements.txt

# TODO python-base-sci needs to package these common elements

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade