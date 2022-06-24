'''/*******************************************************************************
 * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Michael Rabellino
 *******************************************************************************/'''
import pycouchdb
import sys
import logging
import argparse as ap

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    usage = "usage: %prog --host host --username couchdb_username --password couchdb_password"
    parser = ap.ArgumentParser()
    parser.add_argument('--host', dest='host', help='The host name used for the couchdb server')
    parser.add_argument('--username', dest='username', help='The username used to connect to the couchdb server')
    parser.add_argument('--password', dest='password', help='The password used to connect to the couchdb server')
    args = parser.parse_args()

    if args.host == None:
        raise RuntimeError('Unknown couchdb host, check configuration')
    host = args.host

    if args.username == None:
        raise RuntimeError('Unknown couchdb username, check configuration')
    username = args.username

    if args.password == None:
        raise RuntimeError('Unknown couchdb password, check configuration')
    password = args.password

    return host, username, password

if __name__ == '__main__':
    logging.info('Running python test to verify connection to couchdb container')
    try:
        host, username, password = main()

        logging.info('    host: %s', host)
        logging.info('    username: %s', username)
        logging.info('    password: %s', password)

        # build the url for the couchdb
        couch_url = 'http://' + username + ':' + password + '@' + host + ':5984'

        # try to connect
        logging.info('Attempting to connect to couchdb at: %s', couch_url)
        server = pycouchdb.Server(couch_url)

        # print something out from the server to demonstrate connectivity
        logging.info('    connected to the couch server which is running version: %s', server.info()['version'])
    except Exception as e:
        logging.error('Failed to test couchdb driver due to exception: %s', str(e))
    finally:
        logging.info('Test Complete!')