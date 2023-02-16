ARG alpine_version
FROM alpine:"${alpine_version}"

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
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade