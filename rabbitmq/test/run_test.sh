#!/bin/bash

# command line arguments:
#     [1] = rmq server host name
#     [2] = rmq client/server username
#     [3] = rmq client/server password
python ./test_rabbitmq_driver.py "rmqtest" "idss" "password"
