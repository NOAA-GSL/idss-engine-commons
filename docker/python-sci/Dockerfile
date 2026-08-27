# ------------------------------------------------------------------------------
# !!! DON'T CHANGE VERSION NUMBERS* !!!
#   * Managing security vulnerabilities in base images is a challenge and always
#     changing. Any version update to python base should be done so to an image
#     with no known vulnerabilities. Reference docker hub python tags for latest
#     security issues.
#       Also note that just because a base image doesn't have any current known
#       vulnerabilities doesn't mean it won't have any in the future as new
#       vulnerabilities are discovered.
#
# Fixable CVEs
#   - s5cmd:        0.3.3 from September 2025, no long supported?
#                       - 3 CRIT / 20 HIGH, a bulk of our CVEs are from here
# Upstream CVEs
#   from python:3.13.15-alpine3.24:
#   - msgpack:      1.1.2  no fix yet available
#   - setuptools:   70.3.0 no fix yet available
#   from Dockerfile
#   - libssh2:      1.11.1 no fix yet available
#   - binutils:     2.45.1 no fix yet available
# ------------------------------------------------------------------------------
# Use alpine as a base because it's lighter weight, the Debian based images (i.e. slim) have CRIT and HIGH CVEs
# Keep this the same base image as non-sci Dockerfile to reduce CVE blast radius
FROM python:3.13.15-alpine3.24

# setuptools no longer default dependency but is needed to install idsse common code
RUN pip3 install --no-cache --upgrade pip setuptools

# Install build dependencies for pip libraries
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libgcc \
    hdf5-dev \
    netcdf-dev \
    rust \
    cargo

# be careful with apk upgrade, it changes the underlying Alpine library versions underneath 
# the pinned (FROM) version, which may change for better or worse, the CRIT/HIGH CVEs as listed
# from docker hub
RUN apk upgrade --no-cache

# Install explicit system dependency versions ONLY to avoid future breakage
RUN pip3 install --no-cache \
    pika==1.3.1 \
    requests==2.32.5 \
    flask==3.1.3 \
    flask-cors==6.0.2 \
    pint==0.25 \
    pint-xarray==0.6.1 \
    python-dateutil==2.9.0 \
    jsonschema==4.25.1 \
    pycouchdb==1.16.0 \
    gunicorn==25.1.0 \
    geojson==3.2.0 \
    python-logging-rabbitmq==2.0.0 \
    numpy==2.4.2 \
    h5netcdf==1.8.1 \
    h5py==3.15.1 \
    pyproj==3.7.2 \
    jsonschema==4.25.1 \
    geojson==3.2.0 \
    shapely==2.1.2 \
    pillow==12.3.0 \
    scipy==1.17.1 \
    zarr==3.1.5 \
    dask==2026.1.2 \
    xarray==2026.2.0 \
    s3fs==2026.3.0 \
    boto3==1.42.84 \
    obstore==0.11.1 \
    pcodec==1.0.3

RUN pip3 install --no-cache \
    netcdf4==1.7.2 

# Install idsse common python code
WORKDIR /python/idsse_common

COPY ./python/idsse_common /python/idsse_common

RUN python /python/idsse_common/setup.py install

# Run the setup.py
RUN python3 /python/idsse_common/setup.py install