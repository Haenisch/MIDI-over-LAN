# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Logging for the midi_over_lan package.

The name of the logger object is 'midi_over_lan'.

This module defines functions to facilitate logging in the midi_over_lan package.
Logging is done with the standard Python logging module, in particular with the
logging.handlers.QueueHandler class. This class allows to send log messages from
worker processes to the main process, where the log messages are processed in a
separate thread. This approach is especially useful for slow disk I/O operations;
thus, the worker processes can log messages much quicker.

The module provides the following functions:

    init_logger(log_queue: multiprocessing.Queue,
                level: int = logging.CRITICAL) -> logging.Logger:
        Initialize the logger in a worker process. This function must be called
        in each worker process to set up the logger object such that it uses the
        given log queue. Once initialized, the logger can be used as usual. The
        logger name is set to 'midi_over_lan' and the log level is set to the
        given level.

    logger_thread(queue: multiprocessing.Queue):
        Process log messages from the log queue. This function must be called as
        a separate thread in the main process and may only be called once. The
        function starts a logging queue listener that processes log messages
        sent by the worker processes in the background. The thread is stopped by
        putting a 'None' object into the queue.
"""

import logging
import logging.handlers
import multiprocessing


def init_logger(log_queue: multiprocessing.Queue,
                name='midi_over_lan',
                level=logging.CRITICAL) -> logging.Logger:
    """Initialize the logger in a worker process.

    This function must be called in each worker process to set up the logger
    object that uses the given log queue. It should be called as early as
    possible and only once per process. This approach is especially useful for
    slow disk I/O operations; thus, the worker processes can log messages much
    quicker.

    The log queue is a multiprocessing.Queue object that should be instantiated
    in the main process.
    
    Once initialized, the logger can be used as usual. By default, the logger
    name is set to 'midi_over_lan' but can be changed by passing a different
    name (e.g., 'midi_over_lan.sender' or 'midi_over_lan.receiver'). The logger
    is set to propagate messages to the root logger, which is the default
    behavior of the logging module. The log level is set to the given level,
    which is CRITICAL by default. This means that only log messages with a level
    of CRITICAL or higher will be processed.

    Example:
        ```python
        # Spawn a new process and pass the log_queue from the main process.
        # Within the the run() method of the new process, call init_logger().
        logger = init_logger(log_queue, logging.INFO)
        logger.info('This is a log message.')
        ```

    Args:
        log_queue (multiprocessing.Queue): The log queue to send log messages to.
        name (str): The name of the logger. Default is 'midi_over_lan'.
        level (int): The log level to set for the logger. Default is logging.DEBUG.

    Returns:
        logging.Logger: The logger object that uses the given log queue.
    """
    handler = logging.handlers.QueueHandler(log_queue)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def logger_thread(queue: multiprocessing.Queue):
    """Process log messages from the log queue.
    
    This function must be called as a separate thread in the main process and
    may only be called once.
     
    The function starts a logging queue listener that processes log messages
    sent by the worker processes in the background. If the queue is full, the
    worker processes will block until the main process has processed some log
    messages. This is, why the function should be called as early as possible.

    The thread is stopped by putting a 'None' object into the queue.

    How to use:

        ```python
        from midi_over_lan.logging_setup import logger_thread, log_queue

        # At the beginning of the main process
        t = threading.Thread(target=logger_thread, args=(log_queue,))
        t.start()

        # Do some work

        # At the end of the main process
        log_queue.put(None)
        t.join()
        ```
    """
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)
