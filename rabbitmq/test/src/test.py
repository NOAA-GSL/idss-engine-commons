'''/*******************************************************************************
 * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Michael Rabellino
 *******************************************************************************/'''

import pika
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
    # handle command line arguments required to run the event portfolio manager service
    usage = "usage: %prog --host host_name --username rabbitmq_username --password rabbitmq_password"
    parser = ap.ArgumentParser()
    parser.add_argument('--host', dest='host', help='The host name or address of the event portfolio RabbitMQ server to connect to.')
    parser.add_argument('--username', dest='username', help='The username used to connect to the RabbitMQ server (configured by RabbitMQ)')
    parser.add_argument('--password', dest='password', help='The password used to connect to the RabbitMQ server (configured by RabbitMQ)')
    args = parser.parse_args()

    if args.host == None:
        raise RuntimeError('Unknown RabbitMQ host, check configruation')
    host = args.host

    if args.username == None:
        raise RuntimeError('Unknown RabbitMQ username, check configuration')
    username = args.username

    if args.password == None:
        raise RuntimeError('Unknown RabbitMQ password, check configuration')
    password = args.password

    return host, username, password

if __name__ == '__main__':
    logging.info('Running python test to verify connection to RabbitMQ container')
    try:
        host, username, password = main()
        logging.info('    host:     %s', host)
        logging.info('    username: %s', username)
        logging.info('    password: %s', password)

        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
        logging.info('Established connection to RabbitMQ %s', connection)

        channel = connection.channel()

    except Exception as e:
        logging.error('Failed to test RabbitMQ driver due to exception: %s', str(e))
    finally:
        logging.info('Test Complete!')