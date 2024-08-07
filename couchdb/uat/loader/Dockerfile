FROM ghcr.io/noaa-gsl/idss/commons/python/python-base:main

# Install additional dependencies
RUN pip3 install --no-cache \
    cherrypy

COPY couchdb.json couchdb.json
COPY CouchEventPortfolioDB.py CouchEventPortfolioDB.py
COPY Load.py Load.py

COPY EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json
COPY EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json
COPY EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json
COPY EventPort_IDSSe_44444444-aabbccdd-ab87-4808-bd51-a8597e58410d.json /data/EventPort_IDSSe_44444444-aabbccdd-ab87-4808-bd51-a8597e58410d.json

CMD [ "python3", "Load.py"]