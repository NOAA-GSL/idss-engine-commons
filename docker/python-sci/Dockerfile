FROM python:3.13.12-slim

RUN pip3 install --no-cache --upgrade pip \
    pika==1.3.1 \
    python-dateutil==2.9.0 \
    pint==0.25 \
    numpy==2.4.2 \
    netcdf4==1.7.4 \
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
    pcodec==1.0.1 \
    setuptools==82.0.1

# Install idsse common python code
WORKDIR /python/idsse_common

COPY ./python/idsse_common /python/idsse_common

RUN python /python/idsse_common/setup.py install