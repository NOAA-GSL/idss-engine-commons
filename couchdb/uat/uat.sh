#!/bin/sh -xe

# create some basic configurations
cat >/opt/couchdb/etc/local.ini <<EOF
[couchdb]
single_node=true

[admins]
admin = admin
EOF

nohup bash -c "/docker-entrypoint.sh /opt/couchdb/bin/couchdb &"
sleep 15

curl -X PUT http://admin:admin@127.0.0.1:5984/_users
curl -X PUT http://admin:admin@127.0.0.1:5984/_replicator
curl -X PUT http://admin:admin@127.0.0.1:5984/idss  

# this is handled by the loader python script instead
#curl -vX POST http://admin:admin@127.0.0.1:5984/idss -d @- -# -o output -H "Content-Type: application/json" < '{"_id": "_design/event","views": {"idents": {"map": "function(doc) { emit(doc.event.corrId.uuid, doc.event.corrId); }",},"uuids": {"map": "function(doc) { emit(doc.event.corrId.uuid, 1); }","reduce": "function(k,v) {return sum(v); }",},}}'
#curl -vX POST http://admin:admin@127.0.0.1:5984/idss -d @- -# -o output -H "Content-Type: application/json" < EventPort_IDSSe_11111111-beec-467b-a0e6-9d215b715b97_20221223-120000.json
#curl -vX POST http://admin:admin@127.0.0.1:5984/idss -d @- -# -o output -H "Content-Type: application/json" < EventPort_IDSSe_22222222-beec-467b-a0e6-9d215b715b97_20221223-120000.json
#curl -vX POST http://admin:admin@127.0.0.1:5984/idss -d @- -# -o output -H "Content-Type: application/json" < EventPort_IDSSe_33333333-beec-467b-a0e6-9d215b715b97_20221223-120000.json
