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
# Addressing CVE's
#   - s5cmd=0.3.3: this could be problematic, latest release was 0.3.3 from Sept 2025, doesn't
#                  appear to be maintained anymore
# ------------------------------------------------------------------------------
# Use alpine as a base because it's lighter weight, the Debian based images (i.e. slim) have CRIT and HIGH CVEs
# Keep this the same base image as non-sci Dockerfile to reduce CVE blast radius
FROM python:3.13.12-alpine3.23

# setuptools no longer default dependency but is needed to install idsse common code
RUN pip3 install --no-cache --upgrade pip setuptools

# Get the latest package updates to keep security vulnerabilities down
RUN apk update && apk upgrade

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
    s5cmd==0.3.3 \
    shapely==2.1.2 \
    pillow==12.3.0 \
    scipy==1.17.1 \
    zarr==3.1.5 \
    dask==2026.1.2 \
    xarray==2026.2.0 \
    s3fs==2026.3.0 \
    boto3==1.42.84 \
    obstore==0.11.0 \
    pcodec==1.0.3

RUN pip3 install --no-cache \
    netcdf4==1.7.2 

# Install idsse common python code
WORKDIR /python/idsse_common

COPY ./python/idsse_common /python/idsse_common

RUN python /python/idsse_common/setup.py install

# Run the setup.py
RUN python3 /python/idsse_common/setup.py install