# UAT CouchDB - Canned EP.json

Instructions for how to build and run the required utilities to populate a CouchDB with 3 sample Event Portfolios that the DSD is pre-loaded with. Will be used with the EPM Web Service so the DSD can fetch the ep.json instead of hard coding in UI code.

## CouchDB Image
Build the CouchDB image with:

1. `$ cd idss-engine-commons/couchdb/uat`
2. `$ docker build -t idsse/couch/db:uat .`

## EP Loader Image
Build the loader utility with:

1. ` $ cd idss-engine-commons/couchdb/uat/loader`
2. ` $ docker build -t idsse/couch/loader:uat .`

## Run CouchDB
1. Create a test docker network to run services on: `$ docker network create test`
2. In a new terminal window, run the `idsse/couch/db:uat` image with:
  - `$ docker run --rm --name=couchdb-svc-couchdb -it -p 5984:5984 --network=test idsse/couch/db:uat`

## Run CouchDB Loader (if not already loaded)
1. In a new terminal window, run the `idsse/couch/loader:uat` image with:
  - `docker run -it --network=test idsse/couch/loader:uat`

This will populate the running CouchDB container with the 3 event portfolio jsons located in the `idss-engine-commons/couchdb/uat/loader` directory

## Verify CouchDB is loaded and EPM can retrieve EP jsons
1. Start the Event Portfolio Manager Web Service (**NOTE**: The EPM is currently undergoing development, this test is done with the "old" EPM Web Service deployment and may need to change if code is merged to main branch)
  - `docker run --rm --name=epm -p 8080:8080 --network=test idss.engine.service.epm.webservice:local --host rmqserver --username idss --password idss --exchange event_port_exch --couch_host blah --couch_username admin --couch_password admin --couch_db idss`

2. Open a browser window and query the EPM Web Service for the UUIDs it knows about (should be the 3 added by the loader): http://127.0.0.1:8080/uuids

3. Verify the output is: `["22222222-beec-467b-a0e6-9d215b715b97", "11111111-beec-467b-a0e6-9d215b715b97", "33333333-beec-467b-a0e6-9d215b715b97"]`

4. Query the EPM using one of the UUIDs to retrieve the Event Portfolio JSON: http://127.0.0.1:8080/eventportfolio?uuid=11111111-beec-467b-a0e6-9d215b715b97 Should return the json object: `{"corrId": {"originator": "IDSSe", "uuid": "11111111-beec-467b-a0e6-9d215b715b97", "issueDt": "2022-12-23T12:00:00.000Z"}, "issueDt": "2022-12-23T12:00:00.000Z", "location": {"features": [{"type": "Feature", "properties": {"name": "Location 1"}, "geometry": {"coordinates": [[-73.75900245370...`

**NOTE** The EPM Web Service should be able to fetch the persisted EP json except the format of the EP json has changed since the Web Service was developed. The EP Web Service query will throw exceptions because it hasn't been updated to the new format which is currently under development.

## Cleanup
1. Stop EPM Web Service with `ctrl+c` or `command+c`
2. Stop CouchDB with `ctrl+c` or `command+c`
3. Remove Docker test network with: `$ docker network rm test`