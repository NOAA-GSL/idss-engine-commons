Twelve Factors - Logs
=======================

Logs are the stream of aggregated, time-ordered events collected from
the output streams of all running processes and backing services. Logs
in their raw form are typically a text format with one event per line.
Logs have no fixed beginning or end, but flow continuously as long as
the app is operating.

A twelve-factor app never concerns itself with routing or storage of its
output stream. It should not attempt to write to or manage log files.
Instead, each running process writes its event stream, unbuffered, to
stdout. During local development, the developer will view this stream in
the foreground of their terminal to observe the apps behavior.

In staging or production deployments, each process stream will be
captured by the execution environment, collated together with all other
streams from the app, and routed to one or more final destinations for
viewing and long-term archival. These archival destinations are not
visible to or configurable by the app, and instead are completely
managed by the execution environment.

The event stream for an app can be routed to a file, or watched via
realtime tail in a terminal. Most significantly, the stream can be sent
to a log indexing and analysis system such as Elastic Stack / ELK.

Log Levels
==========

Be careful not to log an excessive amount of data. Logs should capture
useful and actionable data. Excessive logging can negatively impact
performance, and it can also increase logging storage and processing
costs. Excessive logging can also result in issues and security events
going undetected.

Application logging frameworks provide different levels of logging, such
as info, debug, or error. For development environments, you might want to
use verbose logging, such as including info and debug, to help your
developers. However, we recommend that you disable info and debug levels
for production environments because these can generate excessive logging
data.

+---------------+---------------------------------------------------------+
| level         | description                                             |
+===============+=========================================================+
| ``DEBUG``     | Debugging purposes for development and troubleshooting  |
+---------------+---------------------------------------------------------+
| ``INFO``      | Something interesting but expected happens (e.g. a new  |
|               | request to download data, creation of a new user, a     |
|               | processing request completed)                           |
+---------------+---------------------------------------------------------+
| ``WARNING``   | Something unexpected or unusual happens. Its not an     |
|               | error, but you should pay attention to it               |
+---------------+---------------------------------------------------------+
| ``ERROR``     | Something that goes wrong but are usually recoverable   |
|               | (e.g. internal exceptions you can handle or APIs        |
|               | returning error results)                                |
+---------------+---------------------------------------------------------+
| ``CRITICAL``  | The application is no longer usable. At this level,     |
|               | someone should be alerted that the system needs         |
|               | immediate attention.                                    |
+---------------+---------------------------------------------------------+

Exclusions
----------
The following attributes should not be recorded directly in the logs.
Remove, mask, sanitize, hash, or encrypt the following:

- Application source code
- Session identification values
- Access tokens
- Sensitive personal data and personally identifiable information (PII)
- Authentication passwords
- Database connection strings
- Encryption keys and other primary secrets

Special Data Types
------------------
Sometimes, the following data can also be recorded in logs. While it can be useful
for investigative and troubleshooting purposes, it can reveal sensitive information
about the system. You might need to anonymize, hash, or encrypt these data types
before the event is recorded:

- File paths
- Internal network names and addresses
- Non-sensitive personal data, such as email addresses

Standards
=========

Logging Utility
---------------

Python includes a standard logging module which shall be used over 3rd
party loggers. This provides a standardized utility accessible to all
applications without needing to install any additional dependencies::

    import logging

Timestamps
-----------

All logging of date and time information shall use the `ISO
8601 <https://www.iso.org/iso-8601-date-and-time-format.html>`__
standard for formatting. All timestamps (event UTC) shall include the
time zone offset so no times are ambiguous. Whenever possible, the
logging of all date time information shall be in Coordinated Universal
Time or UTC; if circumstances in which other time zones are relevant to
the logged information, they shall be indicated with the appropriate
timezone offset.

Examples:

    May 3 2023 1:31 AM UTC >>> ``2020-03-20T01:31:12.467113+00:00``

    July 16 1997 19:20:30 CEST >>> ``1997-07-16T19:20:30.458753+01:00``

UTC to ISO 8601::

    import datetime
    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

>>> ``2023-05-03T01:31:12.467113+00:00``

Local to ISO 8601 with TimeZone information (Python 3)::

    import datetime
    datetime.datetime.now().astimezone().isoformat()

>>> ``2023-05-03T14:32:16.458361+13:00``

Exceptions
-----------

When logging an ERROR caused by an exception, the traceback shall be
included in the log message which is helpful for troubleshooting issues.
As a default, ``logging.error()`` does not include any traceback information
by default – it will simply log the exception as an error, without
providing any additional context. To make sure that ``logging.error()``
captures the traceback, set the ``sys.exc_info`` parameter to ``True``. To
illustrate, lets try logging an exception with and without exc_info::

    def word_count(myfile):
        try:
            # count the number of words in a file and log the result
            [...]
        except OSError as e:
            logger.error(e)
            logger.error(e, exc_info=True)
        [...]

If you run the code with an inaccessible file as the input, it will
generate the following output::

    2023-05-03 16:01:58,191 example - ERROR:[Errno 2] No such file or
    directory: 'nonexistentfile.txt'

    2023-05-03 16:01:58,191 example - ERROR:[Errno 2] No such file or
    directory: 'nonexistentfile.txt'
    Traceback (most recent call last):
        File "/home/rabellino/logstest/example.py", line 14, in word_count
        with open(myfile, 'r') as f:
            FileNotFoundError: [Errno 2] No such file or directory:
                'nonexistentfile.txt'

The first line, logged by ``logger.error()``, doesnt provide much context
beyond the error message (“No such file or directory”). The second line
shows how adding ``exc_info=True`` to ``logger.error()`` allows you to capture
the exception type (``FileNotFoundError``) and the traceback, which includes
information about the function and line number where this exception was
raised.

Alternatively, you can also use ``logger.exception()`` to log the exception
from an exception handler (such as in an except clause). This
automatically captures the same traceback information shown above and
sets ``ERROR`` as the priority level of the log, without requiring you to
explicitly set ``exc_info`` to ``True``

Correlation ID
==============

A correlation ID is a unique ID that is assigned to every transaction.
So, when a transaction becomes distributed across multiple services, we
can follow that transaction across different services using the logging
information. The correlation ID upon generation is effectively passed
from service to service. All services that process that specific
transaction receive the correlation ID and pass it to the next service
and so on so that they can log any events associated with that
transaction to our centralized logs. This helps when we have to
visualize and understand what has happened with this transaction across
different microservices.

The correlation ID shall be included in all relevant transactional
logging statements with exceptions for things such as service
initialization, non-transactional messages, administrative statements,
and general debugging logs.

The correlation ID shall be a semicolon delineated string containing the
following parts:


+------------------+---------------------------------------------------+
| part             | description                                       |
+==================+===================================================+
| ``Origin``       | The service that created the initial correlation  |
|                  | ID                                                |
+------------------+---------------------------------------------------+
| ``UUID``         | A 128-bit universally unique identifier           |
+------------------+---------------------------------------------------+
| ``Issuance``     | A ISO 8601 datetime                               |
| (optional)       |                                                   |
+------------------+---------------------------------------------------+

A UUID is a universally unique identifier that is generated using random
numbers using Pythons built in `uuid version
4 <https://docs.python.org/3/library/uuid.html#uuid.uuid4>`__ library.

To create a UUID::
    
    import uuid
    [...]
    uuid.uuid4()

Acceptable correlation ID formats:

    ``originator;UUID``

        # EPManager;f43513cb-e654-4cdb-afb8-033aeb1701a5

    ``originator;UUID;issueDt``

        # DSD;0e2f7a4a-2826-491b-97da-9721d2257ad7;1997-07-16T19:20:30.45+01:00

Configurations
===============

To follow the best practice of creating a new logger for each module in
your application, use the logging librarys built-in `getLogger()
method <https://docs.python.org/3.11/library/logging.html#logging.getLogger>`__
to dynamically set the logger name to match the name of your module::

    logger = logging.getLogger(__name__)

This ``getLogger()`` method sets the logger name to ``__name__``, which
`corresponds to the fully qualified name of the
module <https://docs.python.org/3/reference/import.html?highlight=__name__#__name__>`__
from which this method is called. This allows you to see exactly which
module in your application generated each log message, so you can
interpret your logs more clearly.

Once you modify the log format to include the logger name ``(%(name)s)``,
youll see this information in every log message.

One of the following default configurations (``DEFALT_LOGGING`` objects
below) shall be applied upon creation of each logger to ensure that each
log statement uses a standard format across all loggers.

Standard logging configuration for Python::

    import logging
    import logging.config

    logger = logging.getLogger(__name__)

    DEFAULT_LOGGING = {} # see below

    logging.config.dictConfig(DEFAULT_LOGGING)

With a Correlation ID
----------------------

configuration::

    DEFAULT_LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)-15s %(name)-5s %(levelname)-8s %(correlation_id)s 
                %(module)s::%(funcName)s(line %(lineno)d) %(message)s'
            },
        },
        'filters': {
            'corr_id: {
                '()': 'idsse.common.correlation_id.AddCorrelationIdFilter',
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'standard',
                'filters': ['corr_id',],
            },
        },
        'loggers': {
            '': {
                'level': 'INFO',
                'handlers': ['default',],
            }
        }
    }

Without a Correlation ID
-------------------------

configuration::

    DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)-15s %(name)-5s %(levelname)-8s
            %(module)s::%(funcName)s(line %(lineno)d) %(message)s'
        },
    },
    'filters': {},
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'standard',
                'filters': [],
            },
        },
        'loggers': {
            '': {
                'level': 'INFO',
                'handlers': ['default',],
            },
        }
    }

Formatting
===========

The formatting of the log record has a number of attributes, most of
which are derived from the parameters upon initialization. The following
attributes shall be part of all standard log messages:

+--------------------+------------------------------------------------------+
| attribute          | description                                          |
+====================+======================================================+
| ``asctime``        | Human-readable time when the log record was created. |
|                    | By default this is an ISO 8601 format, for example:  |
|                    | 2003-07-08 16:49:45                                  |
+--------------------+------------------------------------------------------+
| ``name``           | Name of the logger used to log the call, maps to     |
|                    | __name__                                             |
+--------------------+------------------------------------------------------+
| ``levelname``      | Text logging level for the message (DEBUG, INFO,     |
|                    | WARNING, ERROR, CRITICAL)                            |
+--------------------+------------------------------------------------------+
| ``correlation_id`` | See correlation ID filter above (optional if         |
|                    | non-transactional)         |                         |
+--------------------+------------------------------------------------------+
| ``module``         | Module (name portion of filename)                    |
+--------------------+------------------------------------------------------+
| ``funcName``       | Name of function containing the logging call         |
+--------------------+------------------------------------------------------+
| ``lineno``         | Source line number where the logging was issued      |
+--------------------+------------------------------------------------------+
| ``message``        | The logged message                                   |
+--------------------+------------------------------------------------------+

Example log formatters::

    # with correlation_id
    format= '%(asctime)-15s %(name)-5s %(levelname)-8s %(correlation_id)s
    %(module)s::%(funcName)s(line %(lineno)d) %(message)s'

    # without correlation_id
    format= '%(asctime)-15s %(name)-5s %(levelname)-8s
    %(module)s::%(funcName)s(line %(lineno)d) %(message)s'

Elastic
========

The log stream for all services can be sent to a log indexing,
aggregation, and analysis system such as `Elastic Stack /
ELK <https://www.elastic.co/>`__. The L of the ELK Stack is specific for
Log Monitoring which turns unstructured logs across services into an
asset that can be searched, parsed, and transformed to help identify
common patterns, trends, errors, and event tracing of the entire system.

TODO: screenshots of setting up log filtering on service name and by
correlation_id

Examples
========

basic example::

    import logging
    from idsse.common.log_util import get_default_log_config, set_corr_id

    logger = logging.getLogger(__name__)

    [...]

    def function(json_message):
        # read corr_id from request if possible
        corr_id = get_corr_id(json_message)
        
        if corr_id is not None:
            set_corr_id(*corr_id)
        # else create new corr_id
        else:
            # if uuid is missing, new uuid4 will be created
            set_corr_id('<service name>')
        try:
            # business logic function
            logger.info('Processing request...')
            [...]
        except OSError as e:
            logger.error(e, exc_info=True)
        [...]

    if __name__ == '__main__':
        import logging.config
        logging.config.dictConfig(get_default_log_config('INFO'))
        [...]
