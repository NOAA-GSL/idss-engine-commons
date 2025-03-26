FROM ghcr.io/noaa-gsl/idss/commons/python/python-base:main

# Install additional dependencies
RUN pip install --no-cache \
    pycouchdb

# RUN pip install \
# git+https://github.com/NOAA-GSL/idss-engine-commons@main#subdirectory=python/idsse_common/

COPY ./couchdb/uat/loader/couchdb.json couchdb.json
# COPY ./couchdb/uat/loader/EventPortfolioCouchDb.py EventPortfolioCouchDb.py
# COPY ./couchdb/uat/loader/Load.py Load.py
# COPY ./couchdb/uat/loader/__init__.py __init__.py
COPY ./couchdb/uat/loader/*.py ./

# # Albany
# COPY ./couchdb/uat/loader/EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json
# # Binghamton
# COPY ./couchdb/uat/loader/EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json
# # Syracuse
# COPY ./couchdb/uat/loader/EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json

# # World Cup Events
# COPY ./couchdb/uat/loader/world_cup_ep_1_day.json /data/world_cup_ep_1_day.json
# COPY ./couchdb/uat/loader/world_cup_ep_2_day.json /data/world_cup_ep_2_day.json
# COPY ./couchdb/uat/loader/world_cup_ep_3_day.json /data/world_cup_ep_3_day.json
# COPY ./couchdb/uat/loader/world_cup_ep_4_day.json /data/world_cup_ep_4_day.json
# COPY ./couchdb/uat/loader/world_cup_ep_5_day.json /data/world_cup_ep_5_day.json
# COPY ./couchdb/uat/loader/world_cup_ep_6_day.json /data/world_cup_ep_6_day.json
# COPY ./couchdb/uat/loader/world_cup_ep_7_day.json /data/world_cup_ep_7_day.json

COPY ./couchdb/uat/loader/*.json /data/
# don't try to load CouchDB config json as an event portfolio
RUN rm /data/couchdb.json

CMD [ "python3", "Load.py"]