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
FROM python:3.13.12-slim

# Install explicit system dependency versions ONLY to avoid future breakage
RUN pip3 install --no-cache --upgrade pip \
    pika==1.3.1 \
    python-dateutil==2.9.0 \
    pint==0.25 \
    pint-xarray==0.6.1 \
    numpy==2.4.2 \
    netcdf4==1.7.2 \
    h5netcdf==1.8.1 \
    h5py==3.15.1 \
    pygrib==2.1.8 \
    pyproj==3.7.2 \
    jsonschema==4.25.1 \
    s5cmd==0.3.3 \
    geojson==3.2.0 \
    shapely==2.1.2 \
    pillow==12.1.1 \
    flask==3.1.3 \
    gunicorn==25.1.0 \
    python-logging-rabbitmq==2.0.0 \
    scipy==1.17.1 \
    zarr==3.1.5 \
    dask==2026.1.2 \
    xarray==2026.2.0 \
    s3fs==2026.3.0 \
    boto3==1.42.84 \
    pcodec==1.0.1 \
    setuptools==82.0.1 \
    requests==2.32.5


# Install idsse common python code
WORKDIR /python/idsse_common

COPY ./python/idsse_common /python/idsse_common

RUN python /python/idsse_common/setup.py install