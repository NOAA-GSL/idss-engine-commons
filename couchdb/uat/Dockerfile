FROM couchdb:latest

ENV COUCHDB_USER=admin
ENV COUCHDB_PASSWORD=admin

EXPOSE 5984

COPY startup.sh /usr/local/bin/startup.sh

RUN chmod +x /usr/local/bin/startup.sh

ENTRYPOINT [ "/usr/local/bin/startup.sh" ]