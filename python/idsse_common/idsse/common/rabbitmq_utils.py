"""Module for RabbitMQ client related data classes"""
# ----------------------------------------------------------------------------------
# Created on Fri Sep 8 2023.
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.  (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Paul Hamer (2)
#
# ----------------------------------------------------------------------------------
from typing import NamedTuple


class Conn(NamedTuple):
    """An internal data class for holding the RabbitMQ connection info"""
    host: str
    v_host: str
    port: int
    username: str
    password: str


class Exch(NamedTuple):
    """An internal data class for holding the RabbitMQ exchange info"""
    name: str
    type: str


class Queue(NamedTuple):
    """An internal data class for holding the RabbitMQ queue info"""
    name: str
    route_key: str
    durable: bool
    exclusive: bool
    auto_delete: bool