# ------------------------------------------------------------------------------
# !!! DON'T CHANGE VERSION NUMBERS* !!!
#   * Managing security vulnerabilities in base images is a challenge and always
#     changing. Any version update to python base should be done so to an image
#     with no known vulnerabilities. Reference docker hub python tags for latest
#     security issues.
#       Also note that just because a base image doesn't have any current known
#       vulnerabilities doesn't mean it won't have any in the future as new
#       vulnerabilities are discovered.
# ------------------------------------------------------------------------------
FROM python:3.13.12-alpine3.23

# Install explicit system dependency versions ONLY to avoid future breakage
RUN pip3 install --no-cache \
    pika==1.3.1 \
    requests==2.32.5 \
    flask==3.1.3 \
    pint==0.25 \
    python-dateutil==2.9.0 \
    jsonschema==4.25.1 \
    pycouchdb==1.16.0 \
    gunicorn==25.1.0 \
    geojson==3.2.0 \
    python-logging-rabbitmq==2.0.0 \
    flask-cors==6.0.2 \
    requests==2.32.5

# setuptools no longer default dependency but is needed to install idsse common code
RUN pip3 install --no-cache --upgrade setuptools

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