=======================
Python coding standards
=======================

For Python code style follow `PEP 8`_ plus the guidelines below.

.. _PEP 8: http://www.python.org/dev/peps/pep-0008/

Some good links about Python code style:

- `Guide to Python <http://docs.python-guide.org/en/latest/writing/style/>`_ from Hitchhiker's
- `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html>`_

Use `pylint`_ and `flake8`_ to test for compliance, flake8 also detects some errors,
*with the exception* line length can be extended from 80 to 100 characters

.. _pylint: http://www.logilab.org/857
.. _flake8: http://pypi.python.org/pypi/flake8


Naming Conventions
==================

Names to Avoid
--------------
Avoid using single letter variables, exceptions for iterators such as x,y or i,j. Make sure it will likely be clear to future user.

Never use the characters ‘l’ (lowercase letter el), ‘O’ (uppercase letter oh), or ‘I’ (uppercase letter eye) as single character variable names. In some fonts, these characters are indistinguishable from the numerals one and zero. When tempted to use ‘l’, use ‘L’ instead.

Package and Module Names
------------------------
Modules should have short, all-lowercase names. Underscores can be used in the module name if it improves readability. If a module primarly contains a class the module name should be the lower underscore version of the ClassName (e.g. class_name).

Class Names
-----------
Class names should normally use the CapWords convention.


Type Variable Names
-------------------
Names of type variables should normally use CapWords.

Function and Variable Names
---------------------------
Function names should be lowercase, with words separated by underscores as necessary to improve readability.

Variable names follow the same convention as function names.

Function and Method Arguments
-----------------------------
Always use self for the first argument to instance methods.

Always use cls for the first argument to class methods.

If a function argument’s name clashes with a reserved keyword, it is generally better to append a single
trailing underscore rather than use an abbreviation or spelling corruption. Thus class_ is better than clss. 
(Perhaps better is to avoid such clashes by using a synonym.)

Method Names and Instance Variables
-----------------------------------
Use the function naming rules: lowercase with words separated by underscores as necessary to improve readability.

Use one leading underscore only for non-public methods and instance variables.

To avoid name clashes with subclasses, use two leading underscores to invoke Python’s name mangling rules.

Python mangles these names with the class name: if class Foo has an attribute named __a, it cannot be accessed 
by Foo.__a. (An insistent user could still gain access by calling Foo._Foo__a.) Generally, double leading 
underscores should be used only to avoid name conflicts with attributes in classes designed to be subclassed.


Constants
---------
Constants are usually defined on a module level and written in all capital letters with underscores separating
 words. Examples include MAX_OVERFLOW and TOTAL.


Docstrings
==========
Python uses docstrings to document code. A docstring is a string that is the first statement in a package, 
module, class or function. These strings can be extracted automatically through the __doc__ member of the 
object and are used by pydoc. Always use the three-double-quote """ format for docstrings. 

For more info on docstrings see `Google Docstrings`_

.. _Google Docstrings: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

    def function_docstring(param1: int, param2: str) -> bool:
        """Example function with types documented in the docstring.

        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.
        Returns:
            bool: The return value. True for success, False otherwise.

        Optionally use 'Yields:' for generators, and 'Raises' when exceptions are thrown
        """

Use single quotes
=================

Use single-quotes for string literals, e.g. ``'my-identifier'``, *with the exception* use
double-quotes for strings that are likely to contain single-quote characters as
part of the string itself (such as error messages, or any strings containing
natural language), e.g.  ``"You've got an error!"``.

Single-quotes are easier to read and to type, but if a string contains
single-quote characters then double-quotes are better than escaping the
single-quote characters or wrapping the string in double single-quotes.

Use triple double-quotes for docstrings, see `Docstrings`_.

.. _Docstrings: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

Imports
=======

- Make all imports at the start of the file, after the module docstring.
  Imports should be grouped in the following order:

  1. Standard library imports
  2. Third-party imports
  3. DAS imports

- Within each grouping there should be two section, the first are direct
  import and the second imports using from. 

- Within each section the import should be alphabetized::

    import copy
    import os
    import shutil
    from typing import Dict

    import numpy as np
    from dateutil.parser import parse as dt_parse

    from das_constants import Key
    from netcdf_io import write_netcdf, read_netcdf, read_netcdf_global_attrs
    from utils import to_iso

- Don't use ``from module import *``. Instead list the names you
  need explicitly::

    from module import name1, name2

  Use parenthesis around the names if they are longer than one line::

    from module import (name1, name2, ...
                        name12, name13)

  Or split import from one module onto two lines::

    from module import name1, name2, ...
    from module import name12, name13

Logging
=======

We use `the Python standard library's logging module <https://docs.python.org/2.7/library/logging.html>`_
to log messages, e.g.::

    import logging
    ...
    logger = logging.getLogger(__name__)
    ...
    logger.debug('some debug message')

When logging:

- Keep log messages short.

- Don't include object representations in the log message.  It *is* useful
  to include a domain model identifier where appropriate.

- Choose an appropriate log-level (DEBUG, INFO, ERROR, WARNING or CRITICAL,
  see `Python's Logging HOWTO`_).

.. _Python's Logging HOWTO: http://docs.python.org/2/howto/logging.html

String formatting
=================

Use `Formatted string literals`_ (also called f-strings for short) they let you
include the value of Python expressions inside a string by prefixing the string
with f or F and writing expressions as {expression}.::

    d = datetime.now()
    f'Custom Formatted Date = {d:%m/%d/%Y}'

.. _Formatted string literals: https://docs.python.org/3/tutorial/inputoutput.html#tut-f-strings

Don't use the old ``%s`` style string formatting, e.g. ``"i am a %s" % sub``.
This kind of string formatting is not helpful for internationalization.

Occasionally it might be helpful to use the `str .format() method`_ instead, 
and give meaningful names to each replacement field, for example::

    (' ... {foo} ... {bar} ...').format(foo='foo-value', bar='bar-value')

.. _str .format() method: http://docs.python.org/2/library/stdtypes.html#str.format

Classes
=======

- Class variable: for data shared among all instances.
- Instance variable: for information unique on an instance.
- Regular methods: use "self" to operate on instance.
- Class methods: use to implement alternative constructor (need "cls").
- Static methods: attach functions to class for easy discovery.
- A property(): let getter/setter methods be invoked automatically by attribute access.

Classes should be organized so the most important information is at top, as such:

Class method/function order:
 1. Abstract methods
 2. Magic methods
 3. Class methods as constructors
 4. Properties
 5. Public methods
 6. Static functions
 7. Private method/functions

if "__main__" == __name__:
==========================

Making a Python modules (and .py file) act as the entry point to our Python process.

When making a module runnable add the *if "__main__" == __name__:* as the last block in the file.
In this block import any module need only when running, specify any logging configuration, and 
call a *main()* function::

    if "__main__" == __name__:
        import argparse
        import subprocess
        import sys

        # configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(module)s - %(levelname)s : %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

        main()

The *main()* function should be defined directly about the *if "__main__" == __name__:*. Here 
is where you should handle any input arguments, although you could delegate to a private function
if it improves readability, and code that make this module a script.::

  def main():
    """Ping an amqp url, based on user provided command line arguments"""

    # Handle command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help="Configuration for source and type")
    parser.add_argument('--host', dest='host', required=True,
                        help='The host name or address of the event portfolio RabbitMQ server to connect to.')
    parser.add_argument('--exchange', dest='exchange', default='data.check',
                        help='The name of the exchange channel to publish data availability messages.')
    parser.add_argument('--queue', dest='queue', default='_data.available',
                        help='The name of the queue to publish data availability messages.')
    parser.add_argument('--username', dest='username', default="guest",
                        help='The RabbitMQ server username to use to establish a connection')
    parser.add_argument('--password', dest='password', default="guest",
                        help='The RabbitMQ server password to use to establish a connection')

    args = parser.parse_args()

    # Get connection for publishing the data keys and contents...
    url = (f'amqp://{args.username}:{args.password}@{args.host}:'
           f'5672/%2F?connection_attempts=3&heartbeat=3600')

    ping = subprocess.Popen(["ping", "-c", "4", url],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, error = ping.communicate()
    logging.info(out)
    logging.error(error)

Copyright
=========

Every file should contain a copyright block at the top, after module doc string. 
Typically our contributors are either CIRES, or CIRA. Developer should insure that
the copyright notice included their institution and name. This is an example of 
notice for a file with two contributed, one from each institution. If code has
been developed by employees from one institution, only that institution should
be referenced::

    # ----------------------------------------------------------------------------------
    # Created on Mon Feb 13 2023
    #
    # Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
    # Copyright (c) 2023 Colorado State University. All rights reserved.             (2)
    #
    # Contributors:
    #     Developer1 Name (1)
    #     Developer2 Name (2)
    #
    # ----------------------------------------------------------------------------------


