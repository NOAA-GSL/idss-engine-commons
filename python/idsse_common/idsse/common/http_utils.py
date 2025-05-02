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


class HttpUtils(ProtocolUtils):
    """http Utility Class - Used by DAS for file downloads"""

    def ls(self, path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the http(s) server
        Args:
            path (str): path
            prepend_path (bool): Add path+ to the filename
        Returns:
            Sequence[str]: The results from executing a request get on passed path
        """
        files = []
        try:
            response = requests.get(path, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes

            for line in response.text.splitlines():
                if 'href="' in line:
                    filename = line.split('href="')[1].split('"')[0]

                    # Exclude directories and file without expected suffix
                    if not filename.endswith("/") and filename.endswith(
                        self.path_builder.file_ext
                    ):
                        files.append(filename)

        except requests.exceptions.RequestException as exp:
            if "403" not in str(exp):
                logger.warning("Unable to query supplied Path : %s", str(exp))
            return []
        files = sorted(files, reverse=True)
        if prepend_path:
            return [os.path.join(path, filename) for filename in files]
        return files

    # pylint: disable=unused-argument
    def cp(
        self, path: str, dest: str, concurrency: int | None = None, chunk_size: int | None = None
    ) -> bool:
        """Execute http request download from path to dest.

        Args:
            path (str): Path to the object to be copied
            dest (str): The destination location
            concurrency (optional, int): Number of parallel threads - ignored
            chunk_size (optional, int): Size of chunks (in MB) - ignored
        Returns:
            bool: Returns True if copy is successful
        """
        try:
            with requests.get(path, timeout=5, stream=True) as response:
                # Check if the request was successful
                if response.status_code == 200:
                    # Check that we have a directory to write to...
                    if not os.path.exists(os.path.dirname(dest)):
                        os.makedirs(os.path.dirname(dest))
                    # Open a file in binary write mode
                    with open(dest, "wb") as file:
                        shutil.copyfileobj(response.raw, file)
                    return True

                logger.info("copy fail: request status code: %s", response.status_code)
                return False
        except Exception as e:  # pylint: disable=broad-exception-caught, invalid-name
            logger.error("copy fail: exception %s", str(e))
            return False
