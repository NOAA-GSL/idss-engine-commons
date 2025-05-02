import json
import os
import sys
import cherrypy
from datetime import datetime, timedelta
from typing import AsyncIterator, Dict, Mapping, Tuple, List
from uuid import UUID
import pycouchdb

# configure logging
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)


class CouchEventPortfolioDB(object):

    def __init__(self, config: Dict):
        self.db = None
        self.dbServer = None
        self.hostname = config["hostname"]
        self.username = config["username"]
        self.password = config["password"]
        self.database = config["database"]

        # Set up the database access
        self._connect()
        self._open()
        self._load_views()  # Make sure we have the views we expect for an EventPortfolio
        return

    def _connect(self):
        try:
            self.couch_url = (
                "http://" + self.username + ":" + self.password + "@" + self.hostname + ":5984"
            )
            logging.info("Attempting to connect to couchdb at: %s", self.couch_url)
            self.dbServer = pycouchdb.Server(self.couch_url)
            logging.info("SERVER : %s : %s", str(self.dbServer), str(self.dbServer.info()))

        except Exception as e:
            logging.error("Cannot connect to server {} : {}".format(self.hostname, e))
            raise cherrypy.HTTPError(
                500, message="Unable to connect to server, see logs for details."
            )
        return

    def _open(self):
        try:
            logging.info("Attempting to open an existing database: %s", self.database)
            self.db = self.dbServer.database(self.database)
        except pycouchdb.exceptions.NotFound:
            logging.info("Database not found, attempting to create: %s", self.database)
            self.db = self.dbServer.create(self.database)
        except Exception as e:
            logging.error("Cannot access database {} : {}".format(self.database, e))
            raise cherrypy.HTTPError(
                500, message="Unable to open the database, see logs for details."
            )
        return

    def save_portfolio(
        self,
        event: Dict = None,
    ) -> str:
        if event is None:
            raise cherrypy.HTTPError(500, message="Cannot save an empty event portfolio?")

        # ID is created using the Identifier from the event JSON, get the info required...
        ident = event["corrId"]
        originator = ident["originator"]
        key = ident["uuid"]
        # We can update this after 3.7+ to use datatime.fromisoformat(ident['issueDt'])
        # issueDt = datetime.strptime(ident['issueDt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        issueDt = self._get_isoTime(ident["issueDt"])
        identifier = "_".join(["EventPort", originator, key, issueDt.strftime("%Y%m%d-%H%M%S")])
        try:
            doc = {"_id": identifier, "event": event}
            self.db.save(doc)
            logging.info("Saved %s", identifier)
        except Exception as e:
            logging.warning("Database error : %s", str(e))
            raise cherrypy.HTTPError(
                500, message="Unable to persist event portfolio, see logs for details."
            )
        return ident

    def get_portfolio(self, uuids: str, issue: datetime = None) -> Dict:
        # Handle some of the defaults...
        if issue is None:
            logging.info(
                "get_portfolio issue wasnt set, using default datetime.utcnow() of :%s ",
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            )
            issue = datetime.utcnow()
        else:
            logging.info(
                "get_portfolio issue set by user, using: %s", issue.strftime("%Y-%m-%dT%H:%M:%S")
            )

        if uuids is None or not self.is_valid_uuid(uuids):
            logging.error("You must provide a valid UUID to get a Portfolio? (%s)", uuids)
            raise cherrypy.HTTPError(500, message="Invalid UUID, see logs for details.")

        logging.info("Looking for %s with issue %s", uuids, issue.strftime("%Y-%m-%dT%H:%M:%S"))

        # Collect all the portfolios with the UUID and select the appropriate one from the issue time.
        portfolio = None
        portfolio_id = None
        try:
            for ident in list(self.db.query("event/idents", startkey=uuids, endkey=uuids)):
                logging.info(
                    "Found %s with issue time of %s",
                    ident["id"],
                    self._get_isoTime(ident["value"]["issueDt"]),
                )
                if self._get_isoTime(ident["value"]["issueDt"]) <= issue:
                    portfolio_id = ident["id"]
            if portfolio_id:
                # Retrieve this event portfolio document and return
                logging.info("Fetching event portfolio with uuid: %s", str(portfolio_id))
                portfolio = self.db.get(portfolio_id)["event"]
        except Exception as e:
            logging.warning("Database error : %s", str(e))
            raise cherrypy.HTTPError(
                500, message="Unable to locate event portfolio, see logs for details."
            )

        if not portfolio:
            logging.warning("Unable to locate and/or read requested event portfolio: %s", uuids)
            raise cherrypy.HTTPError(
                404, message="Unable to locate event portfolio, see logs for details."
            )

        logging.info("Returning portfolio json: %s", portfolio)
        return portfolio

    def get_portfolio_valid(
        self,
        issue: datetime = None,
        start: datetime = None,  # Valid start time
        end: datetime = None,  # Valid end time
    ) -> List:

        # Handle some of the defaults...
        if issue is None:
            issue = datetime.utcnow()
        if start is None:
            start = datetime.utcnow()
        if end is None:
            end = start + timedelta(hours=24)
        uuids = []  # Start with an empty list...

        if end < start:
            logging.error("Get portfolio has valid time end is less than the start time?")
            raise cherrypy.HTTPError(
                500, message="Get portfolio has valid time end is less than the start time?"
            )

        for uuid in self.get_uuids():
            # Collect all the UUIDs for the issue time within the appropriate valid window
            portfolio_id = None
            try:
                idents = list(self.db.query("event/idents", startkey=uuid, endkey=uuid))
                for ident in idents:
                    if self._get_isoTime(ident["value"]["issueDt"]) <= issue:
                        portfolio_id = ident["id"]

                if portfolio_id:
                    # Retrieve this event portfolio document and check the valid ranges...
                    portfolio = self.db.get(portfolio_id)["event"]
                    # Only interested in those portfolios with 'timing' field...
                    try:
                        timing = portfolio["timing"]
                        if self._check_valids(timing, start, end):
                            uuids.append(uuid)
                    except Exception as e:
                        # Old format portfolio, no valid time info found. Ignore?
                        logging.debug(
                            "No valid timing found error : %s : %s", str(portfolio_id), str(e)
                        )

            except Exception as e:
                logging.warning("Database error : %s", str(e))
                raise cherrypy.HTTPError(
                    500, message="Unable to locate event portfolio, see logs for details."
                )

        return uuids

    def get_uuids(
        self,
    ) -> List:
        # Query the current cluster for the UUID's from the identifier.key value for each document...
        uuids = set()
        try:
            for ul in list(self.db.query("event/uuids", group="true")):
                uuids.add(ul["key"])
        except Exception as e:
            logging.warning("Database error when getting UUIDs: %s", str(e))
            raise cherrypy.HTTPError(500, message="Database error, see logs for details.")
        return list(uuids)

    def purge_portfolios(self, issue: datetime = None) -> None:
        # Handle some of the defaults...
        if issue is None:
            issue = datetime.utcnow() - timedelta(days=28)

        # Query the current cluster for the UUID's from the identifier.key value for each document...
        try:
            for uuid in self.get_uuids():
                # Check the issue to time to see if this portfolio has expired
                idents = list(self.db.query("event/idents", startkey=uuid, endkey=uuid))
                for ident in idents:
                    if self._get_isoTime(ident["value"]["issueDt"]) <= issue:
                        # Remove this one...
                        logging.info("Purging : %s", ident["id"])
                        self.db.delete(ident["id"])

        except Exception as e:
            logging.warning("Database error when getting UUIDs: %s", str(e))
            raise cherrypy.HTTPError(500, message="Database error, see logs for details.")
        return

    def _load_views(self):
        # The expected querying requires the following views, catch potential conflicts, i.e.
        # the view already exists in database. We attempt load on each instance creation so this
        # is always possible.
        _doc = {
            "_id": "_design/event",
            "views": {
                "idents": {
                    "map": "function(doc) { emit(doc.event.corrId.uuid, doc.event.corrId); }",
                },
                "uuids": {
                    "map": "function(doc) { emit(doc.event.corrId.uuid, 1); }",
                    "reduce": "function(k,v) {return sum(v); }",
                },
            },
        }
        try:
            self.db.save(_doc)
        except pycouchdb.exceptions.Conflict:
            logging.info("Conflict in saving views, assume these are already present in database.")
        return

    @staticmethod
    def is_valid_uuid(uuid, version=4):
        try:
            UUID(uuid, version=version)
        except ValueError:
            return False
        return True

    def _check_valids(self, timing: Dict, start: datetime, end: datetime) -> bool:
        try:
            logging.debug("%s : %s,%s", str(timing), str(start), str(end))

            # Check for validDt list
            valids = timing["validDts"]
            for v in valids:
                if start <= self._get_isoTime(v) <= end:
                    return True
        except Exception as vm:
            logging.debug("validDts missing : ", str(vm))
            # Assume we have startDt/endDt?
            try:
                sDt = timing["startDt"]
                if start <= self._get_isoTime(sDt) <= end:
                    return True
                eDt = timing["endDt"]
                if start <= self._get_isoTime(eDt) <= end:
                    return True
            except Exception as e:
                logging.debug("No valid timing information found? : %s", str(e))

        return False

    @staticmethod
    def _get_isoTime(dtStr: str) -> datetime:
        try:
            isoTime = datetime.strptime(dtStr, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=None)
        except Exception as e:
            logging.error("Could not convert string %s to isoTime? : %s", dtStr, str(e))
            raise cherrypy.HTTPError(
                500, message="Unable to convert string to datetime, see logs for details."
            )
        return isoTime
