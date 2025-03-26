"""Module to get Event Portfolio data in and out of CouchDB"""
# ----------------------------------------------------------------------------------
# Created on Mon Feb 22 2021
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Michael Rabellino (1)
#     Paul Hamer (2)
#     Mackenzie Grimes (2)
#
# ----------------------------------------------------------------------------------

import logging
import logging.config
from datetime import datetime, timedelta, UTC
from typing import NamedTuple

from dateutil.parser import parse as dt_parse, ParserError
from jsonschema.exceptions import ValidationError

from pycouchdb import Server
from pycouchdb.exceptions import Conflict, NotFound
from pycouchdb.client import Database

from idsse.common.validate_schema import get_validator
from idsse.common.utils import is_valid_uuid, to_iso

# configure logger
logger = logging.getLogger('epm.couchdb')


class CouchDbConnectionParams(NamedTuple):
    """Data class to hold connection parameters for couchDB instance"""
    hostname: str
    username: str
    password: str
    database: str


class EventPortfolioCouchDb:
    """This class wraps the interface to couchDB"""
    def __init__(self, config: dict):
        self._db: Database | None = None
        self._db_server: Server | None = None
        self._params = CouchDbConnectionParams(
            hostname=config['hostname'],
            username=config['username'],
            password=config['password'],
            database=config['database']
        )

        # Set up the database access
        self._connect()
        self._open()
        self._load_views()  # Make sure we have the views we expect for an EventPortfolio

        # Get a schema validation for event portfolio messages...
        self._schema_validator = get_validator('event_portfolio_schema')

    def _connect(self):
        """Try to connect couchDB"""
        try:
            couch_url = (f'http://{self._params.username}:{self._params.password}'
                         f'@{self._params.hostname}:5984')
            logger.warning('Attempting to connect to couchdb at: %s', self._params)
            self._db_server = Server(couch_url)
            logger.info('SERVER : %s : %s', str(self._db_server), str(self._db_server.info()))

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Cannot connect to server %s : %s", self._params.hostname, str(exc))
            raise

    def _open(self):
        """Try to open the couchDB database"""
        try:
            logger.info('Attempting to open an existing database: %s', self._params.database)
            self._db = self._db_server.database(self._params.database)
        except NotFound:
            logger.info('Database not found, attempting to create: %s', self._params.database)
            self._db = self._db_server.create(self._params.database)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Cannot access database %s : %s", self._params.database, exc)
            raise

    def save_portfolio(self, event: dict | None = None) -> str:
        """Store an Event Portfolio in the database.
            event: dictionary containing the event portfolio

        Raises:
            ValidationError: if Event Portfolio record is not structured correctly

        Notes:
            Replaces existing portfolios with the same ID (see idsse-963 in linear)

        """
        if event is None:
            raise ValueError('Cannot save an empty event portfolio?')

        # Validate the event portfolio...
        try:
            self._schema_validator.validate(event)
        except ValidationError as exc:
            logger.warning('Unable to persist event portfolio, invalid data: %s', str(exc))
            raise

        # ID is created using the corrId from the event JSON, get the info required...
        ident = event['corrId']
        originator = ident['originator']
        key = ident['uuid']

        issue_dt = dt_parse(ident['issueDt'])
        identifier = '_'.join(['EventPort', originator, key, issue_dt.strftime('%Y%m%d-%H%M%S')])

        # If the document already exists delete it, just ignore NotFound
        try:
            self._db.delete(identifier)
        except NotFound:
            pass
        # Save this document...
        try:
            doc = {'_id': identifier, 'event': event}
            self._db.save(doc)
            logger.info('Saved %s', identifier)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Unable to persist event portfolio. Database error : %s', str(exc))
            raise
        return ident

    def get_portfolio(self, uuid: str, latest_issue_dt: datetime | None = None) -> dict:
        """
        Get DB record of one Event Portfolio identified by UUID.

        Args:
            uuid (str): the UUID of the Event Portfolio in the database
            latestIssueDt (optional, datetime): the latest issueDt to filter
                returned records, ignoring any records with an issueDt after that time.
                If multiple records match, newest DB record will be used.
                Default is None (will use current time as latest possible issueDt).
        """
        # Handle some of the defaults...
        if latest_issue_dt is None:
            logger.debug('get_portfolio: latest_issue_dt was not set, using current time')
            latest_issue_dt = datetime.now(UTC)
        if uuid is None or not is_valid_uuid(uuid):
            logger.error('Invalid UUID to get a Portfolio (%s)', uuid)
            raise ValueError('Invalid UUID, see logs for details.')

        logger.info('Looking for %s with issue %s', uuid, to_iso(latest_issue_dt))

        # Collect all the portfolios matching UUID and select appropriate one based on issueDt.
        portfolio = None
        portfolio_id = None
        try:
            for ident in self._db.query("event/idents", startkey=uuid, endkey=uuid, as_list=True):
                portfolio_issue_dt = dt_parse(ident['value']['issueDt'])
                logger.info('Found %s with issue time of %s', ident['id'],
                            to_iso(portfolio_issue_dt))

                # if this record's issueDt is earlier than latest issueDt requested, save record ID
                if portfolio_issue_dt <= latest_issue_dt:
                    portfolio_id = ident['id']

            if portfolio_id:
                # Retrieve this event portfolio full document and return
                logger.info('Fetching event portfolio with uuid: %s', portfolio_id)
                portfolio = self._db.get(portfolio_id)['event']
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Unable to locate event portfolio. Database error : %s', str(exc))
            raise

        if not portfolio:
            logger.warning('Unable to locate and/or read requested event portfolio: %s', uuid)
            raise ValueError('Unable to locate event portfolio, see logs for details.')

        logger.debug('Returning portfolio json: %s', portfolio)
        return portfolio

    def get_portfolio_with_issue_dt(self, uuid: str, issue_dt: datetime) -> dict:
        """Get DB record of one Event Portfolio identified by UUID and exact issueDt

        Args:
            uuid (str): the UUID of the Event Portfolio in the database
            exact_issue (optional, datetime | None): specific issueDt to filter the returned
                records; guaranteed at most 1 unique record will be found.

        Returns:
            dict: The full Event Portfolio DB record
        """
        if uuid is None or not is_valid_uuid(uuid):
            logger.error('Invalid UUID to get a Portfolio (%s)', uuid)
            raise ValueError('Invalid UUID, see logs for details.')

        portfolio = None
        logger.info('Looking for %s with issue %s', uuid, to_iso(issue_dt))
        try:
            record_key = f'{to_iso(issue_dt)}&{uuid}'
            records = self._db.query("event/uuid-metadata", startkey=record_key, endkey=record_key)

            # Retrieve this event portfolio full document and return
            logger.info('Fetching event portfolio with doc ID: %s', records)
            record = next(records)

            portfolio = self._db.get(record['id'])['event']
            logger.debug('Returning portfolio json: %s', portfolio)
            return portfolio

        except StopIteration as stop_exc:
            logger.warning('Unable to locate requested event portfolio with uuid: %s, issue_dt %s',
                           uuid, issue_dt)
            raise ValueError('Unable to locate event portfolio') from stop_exc

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Unable to locate event portfolio. Database error : %s', str(exc))
            raise

    def get_portfolio_with_valid_dt(
        self,
        issue: datetime | None = None,
        start: datetime | None = None,
        end: datetime | None = None
    ) -> list[dict]:
        """Get list of Event Portfolio records that have a validDt within datetime range

        Args:
            issue (datetime | None): filter records that have issueDt no older than a
                given datetime. Default: current time.
            start (datetime | None): Start of target time range. Default: current time.
            end (datetime | None): End of target time range. Default: start plus 24 hours.
        """
        # Handle some of the defaults...
        if issue is None:
            issue = datetime.now(UTC)
        if start is None:
            start = datetime.now(UTC)
        if end is None:
            end = start + timedelta(hours=24)

        if end < start:
            logger.error('Get portfolio has valid time end is less than the start time?')
            raise ValueError('Cannot get portfolios where end datetime is before start datetime')

        uuids = []  # Start with an empty list...
        logger.info('Looking for portfolios with issueDt %s and validDt between %s and %s',
                    to_iso(issue), to_iso(start), to_iso(end))

        for uuid in self.get_uuids():
            # Collect all the UUIDs for the issue time within the appropriate valid window
            portfolio_id = None
            try:
                idents = self._db.query("event/idents", startkey=uuid, endkey=uuid, as_list=True)
                logger.info('Idents: %s', str(idents))

                # find the first UUID ident earlier than requested issueDt
                for ident in idents:
                    logger.info('ident %s : issue: %s', ident, ident['value']['issueDt'])
                    if dt_parse(ident['value']['issueDt']) <= issue:
                        portfolio_id = ident['id']

                if portfolio_id:
                    logger.info("portfolio_id %s", portfolio_id)
                    # Retrieve this event portfolio document and check the valid ranges...
                    portfolio = self._db.get(portfolio_id)  # ['event']
                    logger.info(str(portfolio['event'].keys()))
                    logger.info(str(portfolio['event']['validDt']))

                    # Only interested in those portfolios with 'timing' field...
                    try:
                        timing = portfolio['event']['validDt']
                        logger.info('validDt %s', str(timing))

                        if self._is_timing_within_range(timing, start, end):
                            uuids.append(uuid)
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        # Old format portfolio, no valid time info found. Ignore?
                        logger.warning('No valid timing found error : %s : %s', str(portfolio_id),
                                       str(exc))

            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.warning('Unable to locate event portfolio. Database error : %s', str(exc))
                raise

        return uuids

    def get_uuids(self) -> list[str]:
        """Get the UUIDs of all portfolios from database as simple string"""
        # Query the current cluster for the UUID's from the identifier.key value for each document
        uuids = set()
        try:
            for record in list(self._db.query("event/uuids", group='true', descending=True)):
                uuids.add(record['key'])
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Database error when getting UUIDs: %s', str(exc))
            raise
        return list(uuids)

    def get_uuids_with_metadata(self) -> list[dict[str, str | None]]:
        """Get the UUIDs (with Event Portfolio names) for all events in the database.

        Returns:
            list[dict[str, str | None]]: a list of Event Portfolio UUIDs with their issueDts
                and names. Note that "name" attribute can be null.
        """
        # Query the current cluster for the UUIDs from the corrId.key value for each document
        try:
            db_results = self._db.query("event/uuid-metadata", as_list=True, descending=True)
            records = [{
                # pull "name" out of Event Portfolio tags (though it may not exist)
                'name': record['value']['name'],
                'issueDt': record['value']['issueDt'],
                'uuid': record['value']['uuid'],
                'nwsOffice': record['value']['office'],
                'startDt': self._get_start_dt(record['value']['validDt']),
                'endDt': self._get_end_dt(record['value']['validDt']),
            } for record in db_results]
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Database error when getting UUIDs: %s', str(exc))
            raise
        return records

    def delete_portfolio(self, uuid: str) -> int:
        """Delete all Event Portfolios matching this UUID

        Returns:
            int: Number of Event Portfolio records that were deleted. If 0, no records were found
        """
        matching_portfolios = set()
        for record in list(self._db.query("event/idents", startkey=uuid, endkey=uuid)):
            try:
                matching_portfolios.add(record['id'])
                self._db.delete(record['id'])
            except (Conflict, NotFound) as exc:
                raise RuntimeError(f'Failed to delete record: {record["key"]}') from exc

        logger.info('Deleted portfolio records: %s', matching_portfolios)
        return len(matching_portfolios)

    def purge_portfolios(self, issue: datetime = None) -> list[str]:
        """Look for any portfolios in the database with an issueDt older than the specified issue,
        and permanently delete them.

        Args:
            issue (datetime): oldest issueDt to persist in the database. Default: 28 days ago.

        Returns:
            list[str]: UUIDs of all Event Portfolios that were deleted.
        """
        # Handle some of the defaults...
        if issue is None:
            issue = datetime.now(UTC) - timedelta(days=28)

        # Query the current cluster for the UUID's from the identifier.key value for each document
        try:
            existing_uuids = self.get_uuids()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Database error when getting UUIDs: %s', str(exc))
            raise

        deleted_uuids: list[str] = []
        for uuid in existing_uuids:
            # Check the issue to time to see if this portfolio has expired
            idents = list(self._db.query("event/idents", startkey=uuid, endkey=uuid))
            for ident in idents:
                if dt_parse(ident['value']['issueDt']) <= issue:
                    # Remove this one...
                    logger.info('Purging : %s', ident['id'])
                    try:
                        self._db.delete(ident['id'])
                        deleted_uuids.append(ident['id'])
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        logger.warning('Failed to delete portfolio %s: %s', ident['id'], str(exc))

        return deleted_uuids

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

                "uuid-metadata": {
                    "map": ("function(doc) { "
                            "const payload = {"
                                "'uuid': doc.event.corrId.uuid, "
                                "'issueDt': doc.event.corrId.issueDt, "
                                "'name': doc.event.tags.keyValues.name, "
                                "'office': doc.event.tags.keyValues.nwsOffice, "
                                "'validDt': doc.event.validDt};"
                            "emit(doc.event.corrId.issueDt + '&' + doc.event.corrId.uuid, "
                            "payload); }"),
                }
            }
        }
        try:
            self._db.save(_doc)
        except Conflict:
            logger.info('Conflict in saving views, now dropping the existing views to save latest')
            # purge the existing views, try to save our application's views again
            try:
                self._db.delete('_design/event')
            except NotFound:
                pass  # no view to delete, yet Conflict?
            self._db.save(_doc)

    @staticmethod
    def _is_timing_within_range(timing: list[dict], start: datetime, end: datetime) -> bool:
        """Returns True if all timing object in a list fall within the provided time range"""
        return all(EventPortfolioCouchDb._is_single_timing_within_range(timing_obj, start, end)
                   for timing_obj in timing)

    @staticmethod
    def _is_single_timing_within_range(timing: dict, start: datetime, end: datetime) -> bool:
        """Returns True if all validDts, or from start to end dt, in a timing object
        fall within the provided time range"""
        try:
            logger.debug('Timing: %s, between start %s and end %s?',
                         str(timing), str(start), str(end))
            # Check for list of explicit times
            valid_dts = timing['times']
            return all(start <= dt_parse(v) <= end for v in valid_dts)
        except (KeyError, ParserError) as valid_error:
            logger.debug('validDts missing : %s', str(valid_error))
            # Assume we have startDt/endDt?
            try:
                start_dt = timing['start']
                end_dt = timing['end']
                return start <= dt_parse(start_dt) <= end and start <= dt_parse(end_dt) <= end
            except (KeyError, ParserError) as exc:
                logger.warning('No valid timing information found? : %s', str(exc))
                return False

    @staticmethod
    def _get_start_dt(timing: dict) -> str | None:
        if len(timing) == 0:
            return None

        first_timing = timing[0]
        try:
            return first_timing['times'][0]
        except KeyError:
            return first_timing['start']

    @staticmethod
    def _get_end_dt(timing: dict) -> str | None:
        if len(timing) == 0:
            return None

        last_timing = timing[-1]
        try:
            return last_timing['times'][-1]
        except KeyError:
            return last_timing['end']
