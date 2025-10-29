# alpine:3.18.6 includes python 3.11.6
#FROM alpine:3.18.6

# reduce python printing to stdout on build
#ENV PYTHONBUFFERED=1

#RUN echo "Installing python" && \
#    apk add --update --no-cache python3 && \
#    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
#    \
#    echo "Installing pip" && \
#    python3 -m ensurepip && \
#    rm -r /usr/lib/python*/ensurepip && \
#    pip3 install --no-cache --upgrade pip setuptools wheel && \
#    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

FROM python:3.12.2-alpine

# install additional packages base packages common among all microservices
RUN pip3 install --no-cache \
    pika==1.3.1 \
    requests==2.32.5 \
    flask==2.3.3 \
    python-dateutil==2.9.0 \
    jsonschema==4.25.1 \
    pycouchdb==1.16.0 \
    gunicorn==22.0.0 \
    geojson==3.2.0 \
    python-logging-rabbitmq==2.0.0 \
    flask-cors==4.0.2

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade

# Install idsse common python code
WORKDIR /python/idsse_common

# Copy the common code
COPY ./python/idsse_common/idsse/common /python/idsse_common/idsse/common
COPY ./docker/python/setup.py /python/idsse_common

# Remove the scientific packages from the base directory
RUN rm -rf /python/idsse_common/sci

# Run the setup.py
RUN python3 /python/idsse_common/setup.py install