"""/*******************************************************************************
* Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
*
* Contributors:
*     Michael Rabellino
*******************************************************************************/"""

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
    handlers=[logging.StreamHandler(sys.stdout)],
)

if "__main__" == __name__:
    logging.info("-----------------------------------------------------------")
    logging.info("Running RabbitMQ test with arguments: " + str(sys.argv))

    host = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    # static test configuration
    network = "rmq-test-network"
    server_image = "idss.engine.commons.rabbitmq.server:test"
    test_image = "idss.engine.commons.rabbitmq.client:test"

    # create a network for the RabbitMQ and event portfolio manager to run on
    try:
        subprocess.check_output("docker network create " + network, shell=True).decode("utf-8")
        logging.info("Created docker network: %s", network)
    except Exception as e:
        logging.warning("Container network already detected, continuing")

    # build the RabbitMQ server container
    try:
        logging.info("Building RabbitMQ server image")
        subprocess.check_output(
            "cd ..; docker build -t " + server_image + " .", shell=True
        ).decode("utf-8")
    except Exception as e:
        logging.warning("Unable to build server container due to exception: %s", str(e))

    # build the test container
    try:
        logging.info("Building test image")
        subprocess.check_output("docker build -t " + test_image + " .", shell=True).decode("utf-8")
    except Exception as e:
        logging.warning("Unable to build test container due to exception: %s", str(e))

    # run the RabbitMQ Server container
    try:
        logging.info("Running the RabbitMQ server container")
        rabbit_mq_docker_server_cmd = (
            "docker run --rm -d --name "
            + host
            + " "
            + "--network "
            + network
            + " -e RABBITMQ_USER="
            + username
            + " -e RABBITMQ_PASSWORD="
            + password
            + " -p 15672:15672 "
            + server_image
        )
        logging.info(rabbit_mq_docker_server_cmd)
        subprocess.check_output(rabbit_mq_docker_server_cmd, shell=True).decode("utf-8")
    except Exception as e:
        logging.warning(
            "Unable to start the RabbitMQ server container due to exception: %s", str(e)
        )

    # allow for some time for the RabbitMQ server to start
    logging.info("Waiting for RabbitMQ server to start...")
    time.sleep(20)

    # verify that RabbitMQ server is running
    try:
        url = "http://localhost:15672"
        logging.info("Checking that RabbitMQ WebUI is running at: %s", url)
        response = urllib.request.urlopen(url)
        response_obj = response.read().decode("utf-8")
        if response_obj.find("Click here to log in") > 0:
            logging.info("  RabbitMQ server is running")
        else:
            logging.warning("  RabbitMQ server didnt start, test may fail...")
    except Exception as e:
        logging.warning(
            "Problem connecting to RabbitMQ WebUI, verify it is running manually at: %s", url
        )

    # run the test container
    try:
        rabbit_mq_docker_test_cmd = (
            "docker run --network "
            + network
            + " "
            + test_image
            + " --host="
            + host
            + " --username="
            + username
            + " --password="
            + password
        )
        os.system(rabbit_mq_docker_test_cmd)
        # subprocess.check_output(rabbit_mq_docker_test_cmd, shell=True).decode('utf-8')
    except Exception as e:
        logging.warning("Unable to run the test container due to exception: %s", str(e))

    # cleanup
    logging.info("-----------")
    logging.info("Cleaning up")

    # stop test server container
    try:
        subprocess.check_output("docker stop " + host, shell=True).decode("utf-8")
        logging.info("Removed test RabbitMQ container: %s", host)
    except Exception as e:
        logging.warning(
            "Unable to stop server container, please stop manually: $ docker stop %s", host
        )
    # remove test server image
    try:
        subprocess.check_output("docker image rm -f " + server_image, shell=True).decode("utf-8")
        logging.info("Removed docker image: %s", server_image)
    except Exception as e:
        logging.warning(
            "Unable to remove server image, please delete manually: $ docker image rm %s",
            server_image,
        )

    # remove test container
    try:
        subprocess.check_output("docker image rm -f " + test_image, shell=True).decode("utf-8")
        logging.info("Removed docker image: %s", test_image)
    except Exception as e:
        logging.warning(
            "Unable to remove test image, please delete manually: $ docker image rm %s", test_image
        )

    # remove docker network
    try:
        subprocess.check_output("docker network rm " + network, shell=True).decode("utf-8")
        logging.info("Removed docker network: %s", network)
    except Exception as e:
        logging.warning(
            "Unable to remove container network, please delete manually: $ docker network rm %s",
            network,
        )

    logging.info("Done")
    logging.info("-----------------------------------------------------------")
