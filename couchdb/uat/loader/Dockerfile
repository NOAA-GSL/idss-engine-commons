FROM ghcr.io/noaa-gsl/idss/commons/python/python-base:main

# Install additional dependencies
RUN pip3 install --no-cache \
    cherrypy

COPY ./couchdb/uat/loader/couchdb.json couchdb.json
COPY ./couchdb/uat/loader/CouchEventPortfolioDB.py CouchEventPortfolioDB.py
COPY ./couchdb/uat/loader/Load.py Load.py

# Albany
#COPY ./couchdb/uat/loader/EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json
# Binghamton
#COPY ./couchdb/uat/loader/EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json
# Syracuse
#COPY ./couchdb/uat/loader/EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json /data/EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json

# World Cup Events
#COPY ./couchdb/uat/loader/world_cup_ep_1_day.json /data/world_cup_ep_1_day.json
#COPY ./couchdb/uat/loader/world_cup_ep_2_day.json /data/world_cup_ep_2_day.json
#COPY ./couchdb/uat/loader/world_cup_ep_3_day.json /data/world_cup_ep_3_day.json
#COPY ./couchdb/uat/loader/world_cup_ep_4_day.json /data/world_cup_ep_4_day.json
#COPY ./couchdb/uat/loader/world_cup_ep_5_day.json /data/world_cup_ep_5_day.json
#COPY ./couchdb/uat/loader/world_cup_ep_6_day.json /data/world_cup_ep_6_day.json
#COPY ./couchdb/uat/loader/world_cup_ep_7_day.json /data/world_cup_ep_7_day.json

# Other Events
COPY ./couchdb/uat/loader/Atlanta_Airshow_2025Jun30.json /data/Atlanta_Airshow_2025Jun30.json
COPY ./couchdb/uat/loader/Buckley_AFB_cloud_ceiling_2025Apr29.json /data/Buckley_AFB_cloud_ceiling_2025Apr29.json
COPY ./couchdb/uat/loader/Charleston_Snow_2025Jan22.json /data/Charleston_Snow_2025Jan22.json
COPY ./couchdb/uat/loader/Corpus_Christi_Navy_Air_Station_Thunder.json /data/Corpus_Christi_Navy_Air_Station_Thunder.json
COPY ./couchdb/uat/loader/Duluth_I35_Winter_Storm_2025Apr02.json /data/Duluth_I35_Winter_Storm_2025Apr02.json
COPY ./couchdb/uat/loader/GSL_Test_1_2025May15.json /data/GSL_Test_1_2025May15.json
COPY ./couchdb/uat/loader/Palisades_Fire_2025Jan10.json /data/Palisades_Fire_2025Jan10.json
COPY ./couchdb/uat/loader/Pittsburgh_US_Open_2025Jun9.json /data/Pittsburgh_US_Open_2025Jun9.json

CMD [ "python3", "Load.py"]