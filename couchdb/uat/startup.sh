#!/bin/sh

# create some basic configurations
cat >/opt/couchdb/etc/local.ini <<EOF
[couchdb]
single_node=true

[admins]
admin = admin
EOF

#nohup bash -c "/docker-entrypoint.sh /opt/couchdb/bin/couchdb &"
#sleep 5

# Start CouchDB in the background
/opt/couchdb/bin/couchdb &

# Wait for CouchDB to start
until curl -s http://127.0.0.1:5984/_up; do
  echo "Waiting for CouchDB to start..."
  sleep 1
done

# Curl the _users table
echo "Curling the _users table..."
curl -s -u $COUCHDB_USER:$COUCHDB_PASSWORD http://127.0.0.1:5984/_users

# Curl the _replicator table
echo "Curling the _replicator table..."
curl -s -u $COUCHDB_USER:$COUCHDB_PASSWORD http://127.0.0.1:5984/_replicator

# Bring CouchDB to the foreground
wait



#!/bin/sh -xe



#curl -X PUT http://admin:admin@127.0.0.1:5984/_users
#curl -X PUT http://admin:admin@127.0.0.1:5984/_replicator
#curl -X PUT http://admin:admin@127.0.0.1:5984/idss  

# Bring CouchDB to the foreground
#wait

# this is handled by the loader python script instead