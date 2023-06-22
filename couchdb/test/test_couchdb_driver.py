'''/*******************************************************************************
 * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Michael Rabellino
 *******************************************************************************/'''

import os
import sys
import logging
import time
import subprocess
import urllib, urllib.request

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

if '__main__' == __name__:
    logging.info('-----------------------------------------------------------')
    logging.info('Running couchdb test with arguments: ' + str(sys.argv))

    host = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    # static test configuration
    network = 'couch-test-network'
    server_image = 'idss.engine.commons.couchdb.server:test'
    test_image = 'idss.engine.commons.couchdb.client:test'

    # create a network for the couchdb server and test to run on
    try:
        subprocess.check_output('docker network create ' + network, shell=True).decode('utf-8')
        logging.info('Created docker network: %s', network)
    except Exception as e:
        logging.warning('Container network already detected, continuing')

    # build the couchdb server container
    try:
        logging.info('Building couchdb server image')
        subprocess.check_output('cd ..; docker build -t ' + server_image + ' .', shell=True).decode('utf-8')
    except Exception as e:
        logging.warning('Unable to build server container due to exception: %s', str(e))

    # build the test container
    try:
        logging.info('Building test image')
        subprocess.check_output('docker build -t ' + test_image + ' .', shell=True).decode('utf-8')
    except Exception as e:
        logging.warning('Unable to build test container due to exception: %s', str(e))
    
    # run the couchdb server container
    try:
        logging.info('Running the couchdb server container')
        couchdb_docker_server_cmd = (
            'docker run --rm -d --name ' + host + ' ' +
            '--network ' + network + ' ' +
            '-e COUCHDB_USER=' + username + ' ' +
            '-e COUCHDB_PASSWORD=' + password + ' ' +
            '-p 5984:5984 ' +
            server_image
        )
        logging.info(couchdb_docker_server_cmd)
        subprocess.check_output(couchdb_docker_server_cmd, shell=True).decode('utf-8')
    except Exception as e:
        logging.warning('Unable to start the couchdb server container due to exception: %s', str(e))

    # allow for some time for the couchdb server to start
    logging.info('Waiting for couchdb server to start...')
    time.sleep(10)

    # run the test container
    try:
        logging.info('Running the test container')
        couchdb_docker_test_cmd = (
            'docker run --network ' + network + ' ' +
            test_image + ' ' +
            '--host=' + host + ' ' +
            '--username=' + username + ' ' +
            '--password=' + password + ' '
        )
        logging.info(couchdb_docker_test_cmd)
        os.system(couchdb_docker_test_cmd)
    except Exception as e:
        logging.warning('Unable to run the test container due to exception: %s', str(e))

    # cleanup
    logging.info('-----------')
    logging.info('Cleaning up')

    # stop test server container
    try:
        subprocess.check_output('docker stop ' + host, shell=True).decode('utf-8')
        logging.info('Removed test couchdb container: %s', host)
    except Exception as e:
        logging.warning('Unable to stop server container, please stop manually: $ docker stop %s', host)
    # remove test server image
    try:
        subprocess.check_output('docker image rm -f ' + server_image, shell=True).decode('utf-8')
        logging.info('Removed docker image: %s', server_image)
    except Exception as e:
        logging.warning('Unable to remove server image, please delete manually: $ docker image rm %s', server_image)

    # remove test container
    try:
        subprocess.check_output('docker image rm -f ' + test_image, shell=True).decode('utf-8')
        logging.info('Removed docker image: %s', test_image)
    except Exception as e:
        logging.warning('Unable to remove test image, please delete manually: $ docker image rm %s', test_image)

    # remove docker network
    try:
        subprocess.check_output('docker network rm ' + network, shell=True).decode('utf-8')
        logging.info('Removed docker network: %s', network)
    except Exception as e:
        logging.warning('Unable to remove container network, please delete manually: $ docker network rm %s', network)
    

    logging.info('Done')
    logging.info('-----------------------------------------------------------')

