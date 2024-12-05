"""Helper function for listing directories and retrieving s3 objects"""
# -------------------------------------------------------------------------------
# Created on Tue Dec 3 2024
#
# Copyright (c) 2023 Colorado State University. All rights reserved.             (1)
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (2)
#
# Contributors:
#     Paul Hamer (1)
#
# -------------------------------------------------------------------------------
import logging
import os
import shutil
from collections.abc import Sequence

import requests

from .protocol_utils import ProtocolUtils

logger = logging.getLogger(__name__)

# pylint: disable=broad-exception-caught

class HttpUtils(ProtocolUtils):
    """http Utility Class - Used by DAS for file downloads"""


    def ls(self, url: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the http(s) server
        Args:
            url (str): URL
            prepend_path (bool): Add URL+ to the filename
        Returns:
            Sequence[str]: The results from executing a request get on passed url
        """
        try:
            files = []
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes

            for line in response.text.splitlines():
                if 'href="' in line:
                    filename = line.split('href="')[1].split('"')[0]

                    if not filename.endswith('/'):  # Exclude directories
                        files.append(filename)

        except requests.exceptions.RequestException as exp:
            logger.warning('Unable to query supplied URL: %s', str(exp))
            return []
        if prepend_path:
            return [os.path.join(url, filename) for filename in files]
        return files


    def cp(self, path: str, dest: str) -> bool:
        """Execute http request download from path to dest.

        Args:
            path (str): Path to the object to be copied
            dest (str): The destination location
        Returns:
            bool: Returns True if copy is successful
        """
        try:
            with requests.get(os.path.join(path), timeout=5, stream=True) as response:
                # Check if the request was successful
                if response.status_code == 200:
                    # Open a file in binary write mode
                    with open(dest, "wb") as file:
                        shutil.copyfileobj(response.raw, file)
                    return True

                logger.debug('copy fail: request status code: %s', response.status_code)
                return False
        except Exception:  # pylint: disable=broad-exception-caught
            return False
