FROM alpine:3.12

# reduce python printing to stdout on build
ENV PYTHONBUFFERED=1

RUN echo "Installing python" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "Installing pip" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

# install additional packages base packages common among all microservices
RUN pip3 install --no-cache \
    pika==1.3.1 \
    requests==2.28.2 \
    cherrypy==18.8.0 \
    python-dateutil==2.8.2 \
    pycouchdb==1.14.2

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade